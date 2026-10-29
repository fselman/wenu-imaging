/* Retained per-fd observer from accepted BPM harness; test-only POSIX code. */
/* #116: record each identity without opening files or changing the gate.
 * Target lookup is explanatory: unsupported socket/pipe paths remain explicit. */
static void descriptor_detail(const char *phase, int fd, int flags,
                              const struct stat *info)
{
    char target[PATH_MAX];
    int found, error;
#if defined(__linux__)
    char linkpath[64];
    ssize_t length;
#endif
    fprintf(stderr,
            "DESCRIPTOR DETAIL phase=%s fd=%d flags=%d dev=%lu ino=%lu mode=%lu\n",
            phase, fd, flags, (unsigned long)info->st_dev,
            (unsigned long)info->st_ino, (unsigned long)info->st_mode);
    found = 0;
    error = 0;
#if defined(__APPLE__) && defined(F_GETPATH)
    if (fcntl(fd, F_GETPATH, target) == 0) found = 1;
    else error = errno;
#elif defined(__linux__)
    sprintf(linkpath, "/proc/self/fd/%d", fd);
    length = readlink(linkpath, target, sizeof(target) - 1);
    if (length >= 0) {
        target[length] = '\0';
        found = 1;
    } else error = errno;
#endif
    if (found)
        fprintf(stderr, "DESCRIPTOR TARGET phase=%s fd=%d path=%s\n", phase, fd, target);
    else
        fprintf(stderr, "DESCRIPTOR TARGET phase=%s fd=%d unavailable_errno=%d\n", phase, fd, error);
}

/* Enumerate open descriptors independently of the soft limit: the production
 * allocator raises that limit on first use (#106). Exclude only this scan's
 * temporary directory descriptor; close it before returning. */
static int descriptors(const char *phase, unsigned long *identity)
{
    DIR *directory;
    struct dirent *item;
    struct stat info;
    const char *location;
    char *end;
    long number;
    int fd, flags, count, scan_fd, failed;
    unsigned long value, cell;
#if defined(__APPLE__)
    location = "/dev/fd";
#elif defined(__linux__)
    location = "/proc/self/fd";
#else
    fprintf(stderr, "DESCRIPTORS ERROR unsupported platform\n");
    return -1;
#endif
    directory = opendir(location);
    if (directory == NULL) {
        fprintf(stderr, "DESCRIPTORS ERROR opendir errno=%d\n", errno);
        return -1;
    }
    scan_fd = dirfd(directory);
    failed = scan_fd < 0;
    count = 0;
    value = 0;
    while (!failed) {
        errno = 0;
        item = readdir(directory);
        if (item == NULL) {
            failed = errno != 0;
            break;
        }
        number = strtol(item->d_name, &end, 10);
        if (end == item->d_name || *end != '\0') continue;
        if (errno == ERANGE || number < 0 || number > INT_MAX) {
            failed = 1;
            break;
        }
        fd = (int)number;
        if (fd == scan_fd) continue;
        flags = fcntl(fd, F_GETFD);
        if (flags < 0 || fstat(fd, &info) != 0) {
            fprintf(stderr, "DESCRIPTORS ERROR inspect fd=%d errno=%d\n", fd, errno);
            failed = 1;
            break;
        }
        descriptor_detail(phase, fd, flags, &info);
        count++;
        cell = (unsigned long)fd;
        cell = cell * 33UL + (unsigned long)flags;
        cell = cell * 33UL + (unsigned long)info.st_dev;
        cell = cell * 33UL + (unsigned long)info.st_ino;
        cell = cell * 33UL + (unsigned long)info.st_mode;
        value += cell; /* Enumeration order is not an ownership property. */
    }
    if (closedir(directory) != 0) failed = 1;
    if (failed) {
        fprintf(stderr, "DESCRIPTORS ERROR incomplete enumeration\n");
        return -1;
    }
    fprintf(stderr, "DESCRIPTOR SET phase=%s count=%d identity=%lu\n", phase, count, value);
    fflush(stderr);
    *identity = value;
    return count;
}

static void descriptor_limit(const char *phase)
{
    struct rlimit limit;
    if (getrlimit(RLIMIT_NOFILE, &limit) == 0)
        printf("DESCRIPTOR LIMIT %s soft=%lu hard=%lu soft_unlimited=%d\n",
               phase, (unsigned long)limit.rlim_cur, (unsigned long)limit.rlim_max,
               limit.rlim_cur == RLIM_INFINITY);
    else
        fprintf(stderr, "DESCRIPTOR LIMIT ERROR %s errno=%d\n", phase, errno);
}

