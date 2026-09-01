/* Copyright (c) 2004-2009, Sara Golemon <sarag@libssh2.org>
 * Copyright (c) 2009-2015 Daniel Stenberg
 * Copyright (c) 2010 Simon Josefsson <simon@josefsson.org>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *   Redistributions of source code must retain the above
 *   copyright notice, this list of conditions and the
 *   following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above
 *   copyright notice, this list of conditions and the following
 *   disclaimer in the documentation and/or other materials
 *   provided with the distribution.
 *
 *   Neither the name of the copyright holder nor the names
 *   of any other contributors may be used to endorse or
 *   promote products derived from this software without
 *   specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
 * USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 */

static char* ERRORNAMES[] = {
"NONE",//                  0
"SOCKET_NONE",  // -1
"BANNER_NONE",  // -2
"BANNER_SEND",  // -3
"INVALID_MAC",  // -4
"KEX_FAILURE",  // -5
"ALLOC",  // -6
"SOCKET_SEND",  // -7
"KEY_EXCHANGE_FAILURE",  // -8
"TIMEOUT",  // -9
"HOSTKEY_INIT",  // -10
"HOSTKEY_SIGN",  // -11
"DECRYPT",  // -12
"SOCKET_DISCONNECT",  // -13
"PROTO",  // -14
"PASSWORD_EXPIRED",  // -15
"FILE",  // -16
"METHOD_NONE",  // -17
"PUBLICKEY_UNRECOGNIZED",  // -18
"PUBLICKEY_UNVERIFIED",  // -19
"CHANNEL_OUTOFORDER",  // -20
"CHANNEL_FAILURE",  // -21
"CHANNEL_REQUEST_DENIED",  // -22
"CHANNEL_UNKNOWN",  // -23
"CHANNEL_WINDOW_EXCEEDED",  // -24
"CHANNEL_PACKET_EXCEEDED",  // -25
"CHANNEL_CLOSED",  // -26
"CHANNEL_EOF_SENT",  // -27
"SCP_PROTOCOL",  // -28
"ZLIB",  // -29
"SOCKET_TIMEOUT",  // -30
"SFTP_PROTOCOL",  // -31
"REQUEST_DENIED",  // -32
"METHOD_NOT_SUPPORTED",  // -33
"INVAL",  // -34
"INVALID_POLL_TYPE",  // -35
"PUBLICKEY_PROTOCOL",  // -36
"EAGAIN",  // -37
"BUFFER_TOO_SMALL",  // -38
"BAD_USE",  // -39
"COMPRESS",  // -40
"OUT_OF_BOUNDARY",  // -41
"AGENT_PROTOCOL",  // -42
"SOCKET_RECV",  // -43
"ENCRYPT",  // -44
"BAD_SOCKET",  // -45
"KNOWN_HOSTS",  // -46
"CHANNEL_WINDOW_FULL",  // -47 
};

