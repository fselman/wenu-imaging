/*----------------------------------------------------------------------------*/
/**
   @file	qerror.c
   @author	N. Devillard
   @date	Aug 2001
   @version	$Revision: 1.9 $
   @brief

   This module is responsible for error message display. It allows
   to re-direct all messages to a given set of functions for display.
*/
/*----------------------------------------------------------------------------*/

/*
	$Id: qerror.c,v 1.9 2005/05/18 14:38:01 yjung Exp $
	$Author: yjung $
	$Date: 2005/05/18 14:38:01 $
	$Revision: 1.9 $
*/

/*-----------------------------------------------------------------------------
   								Includes
 -----------------------------------------------------------------------------*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>

/*-----------------------------------------------------------------------------
   								Defines
 -----------------------------------------------------------------------------*/
/* Max number of error handling functions registered */
#define QFITS_ERR_MAXERRDISP		8
/* Max size of an error message */
#define QFITS_ERR_MSGSIZE			1024

/*-----------------------------------------------------------------------------
   							Private stuff
 -----------------------------------------------------------------------------*/

/* Type of a display function only defined for legibility here */
typedef void (*qfits_err_dispfunc)(char *) ;
/* Default display function prints out msg to stderr */
static void qfits_err_display_stderr(char * s)
{ fprintf(stderr, "qfits: %s\n", s); }
/* Static control structure, completely private */
static struct {
	qfits_err_dispfunc 	disp[QFITS_ERR_MAXERRDISP] ;
	int 				n ;
	int					active ;
} qfits_err_control = {{qfits_err_display_stderr}, 1, 0} ;

/*-----------------------------------------------------------------------------
  							Function codes
 -----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------*/
/**
  @brief    used for message display
  @param    msg     message
  @return   nothing
  It calls registered display functions one after another.
 */
/*----------------------------------------------------------------------------*/
static void qfits_err_main_display(char * msg)
{
	int	i ;

	/* Check if there is a message in input */
	if (msg==NULL)
		return ;

	/* Loop on all registered functions and call them */
	for (i=0 ; i<qfits_err_control.n ; i++) {
		if (qfits_err_control.disp[i]) {
			qfits_err_control.disp[i](msg);
		}
	}
	return ;
}

/*----------------------------------------------------------------------------*/
/**
  @brief	Get the current status of error display.
  @return	int 1 if error display is active, 0 if not.

  This function returns the current error display status. If it returns 1,
  it means that all calls to qfits_error/qfits_warning will display
  messages using the registered functions, otherwise they do nothing.
 */
/*----------------------------------------------------------------------------*/
int qfits_err_statget(void)
{
	return qfits_err_control.active ;
}

/*----------------------------------------------------------------------------*/
/**
  @brief	Set the current status of error display.
  @param	sta		New status to be set.
  @return	int giving the previous display status.

  This function sets the current error display status to the required
  value, and returns the previous value. It is useful to store the
  previous value, in view of restoring it afterwards, e.g. to make a
  function silent on all its errors. Example:

  @code
  int prev_stat = qfits_err_statset(0) ;
  function_call() ;
  qfits_err_statset(prev_stat);
  @endcode
 */
/*----------------------------------------------------------------------------*/
int qfits_err_statset(int sta)
{
	int prev ;
	prev = qfits_err_control.active ;
	qfits_err_control.active=sta ;
	return prev ;
}

/*----------------------------------------------------------------------------*/
/**
  @brief	Register a function to display error/warning messages.
  @param	dispfn	Display function (see doc below).
  @return	int 0 if function was registered, -1 if not.

  This function registers a display function into the error-handling
  module. Display functions have the following prototype:

  @code
  void display_function(char * msg);
  @endcode

  They are simple functions that expect a ready-made error message
  and return void. They can do whatever they want with the message
  (log it to a file, send it to a GUI, to the syslog, ...). The
  message is built using a printf-like statement in qfits_error and
  qfits_warning, then passed to all registered display functions.

  A maximum of QFITS_ERR_MAXERRDISP can be registered (see source code).
  If the limit has been reached, this function will signal it by
  returning -1.
 */
/*----------------------------------------------------------------------------*/
int qfits_err_register(qfits_err_dispfunc dispfn)
{
	if (qfits_err_control.n==QFITS_ERR_MAXERRDISP) {
		/* Cannot register any more function */
		return -1 ;
	}
	qfits_err_control.disp[qfits_err_control.n] = dispfn ;
	qfits_err_control.n ++ ;
	return 0 ;
}

/* Public warning/error functions. Diagnostics may be shortened, but never
 * silently: ordinary messages retain exact prefixes/bytes. Refs #74. */
static void qfits_message(const char *prefix, const char *fmt, va_list ap)
{
    char all[QFITS_ERR_MSGSIZE];
    const char marker[] = "...[truncated]";
    size_t offset;
    int count;
    offset = strlen(prefix);
    memcpy(all, prefix, offset);
    count = vsnprintf(all + offset, sizeof(all) - offset, fmt, ap);
    if (count < 0) strcpy(all + offset, "[format error]");
    else if ((size_t)count >= sizeof(all) - offset)
        memcpy(all + sizeof(all) - sizeof(marker), marker, sizeof(marker));
    qfits_err_main_display(all);
}
void qfits_warning(const char *fmt, ...)
{
    va_list ap;
    if (qfits_err_control.active == 0) return;
    va_start(ap, fmt); qfits_message("*** ", fmt, ap); va_end(ap);
}
void qfits_error(const char *fmt, ...)
{
    va_list ap;
    if (qfits_err_control.active == 0) return;
    va_start(ap, fmt); qfits_message("error: ", fmt, ap); va_end(ap);
}

/* vim: set ts=4 et sw=4 tw=75 */
