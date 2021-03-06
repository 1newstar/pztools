#!/bin/bash
#
#	BakaSQL (formerly web query executor )
#	riccardo.pizzi@lastminute.com Jan 2015
#
VERSION="1.10.3"
HOSTFILE=/etc/bakasql.conf
BASE=/usr/local/bakasql
MIN_REQ_CARDINALITY=5
MAX_QUERY_SIZE=65535
BAKAUTILS=$BASE/sbin/bakautils
#
set -f
post=0
post_error=0
dryrun=0
skip_checks=0
db=""
kill_backq=0
speed_hacks=0
periodic_commit=0
committed_something=0
commit_interval=1000
ninja=0
enable_ninja=0
default_db=""
closing_tags="</FONT></BODY></HTML>"
total_warnings=0
total_errors=0
last_last_id=0
last_aitable=""
tmpf=/tmp/bakasql.$$
warnings_tmpf=/tmp/bakasql.warn.$$
errors_tmpf=/tmp/bakasql.err.$$
output_tmpf=/tmp/bakasql.out.$$
cached_db_tmpf=/tmp/bakasql.cdb.$$
dump_tmpf=/tmp/bakasql.dmp.$$
rows_tmpf=/tmp/bakasql.row.$$
vars_tmpf=/tmp/bakasql.vars.$$
cmlog_tmpf=/tmp/bakasql.cmlog.$$
totcnt_tmpf=/tmp/bakasql.totcnt.$$
cardinfo_tmpf=/tmp/bakasql.crdinf.$$
resultset_tmpf=/tmp/bakasql.result.$$
resultset2_tmpf=/tmp/bakasql.result2.$$
w_resultset_tmpf=/tmp/bakasql.wresult.$$
query_tmpf=/tmp/bakasql.query.$$
explain_tmpf=/tmp/bakasql.explain.$$
trap 'rm -f $tmpf $warnings_tmpf $errors_tmpf $output_tmpf $cached_db_tmpf $dump_tmpf $rows_tmpf $vars_tmpf $cmlog_tmpf $totcnt_tmpf $cardinfo_tmpf $resultset_tmpf $w_resultset_tmpf $resultset2_tmpf $query_tmpf $explain_tmpf' 0

unescape_input()
{
	echo "$1" | sed -e "s/%24/$/g" -e "s/%40/@/g" -e "s/%21/!/g" -e "s/%3F/?/g" -e "s/%60/\`/g" -e "s/+/ /g" -e "s/%3D/=/g" -e "s/%2B/+/g" -e "s/%3B/;/g" -e "s/%27/'/g" -e "s/%3A/:/g" -e "s/%28/(/g" -e "s/%29/)/g" -e "s/%2C/,/g" -e "s/%23/#/g" -e "s/%22/\"/g" -e "s/%3C/</g" -e "s/%2F/\//g" -e "s/%3E/>/g" -e "s/%26/\&/g" -e "s/%7B/{/g" -e "s/%7D/}/g" -e "s/%5B/[/g" -e "s/%5D/]/g" -e "s/%5C/\\\/g" -e "s/%25/%/g" -e "s/%7C/|/g" -e "s/%09/ /g" -e "s/%7E/~/g" -e "s/%80/\\x80/g" -e "s/%81/\\x81/g" -e "s/%82/\\x82/g" -e "s/%83/\\x83/g" -e "s/%84/\\x84/g" -e "s/%85/\\x85/g" -e "s/%86/\\x86/g" -e "s/%87/\\x87/g" -e "s/%88/\\x88/g" -e "s/%89/\\x89/g" -e "s/%8A/\\x8A/g" -e "s/%8B/\\x8B/g" -e "s/%8C/\\x8C/g" -e "s/%8D/\\x8D/g" -e "s/%8E/\\x8E/g" -e "s/%8F/\\x8F/g" -e "s/%90/\\x90/g" -e "s/%91/\\x91/g" -e "s/%92/\\x92/g" -e "s/%93/\\x93/g" -e "s/%94/\\x94/g" -e "s/%95/\\x95/g" -e "s/%96/\\x96/g" -e "s/%97/\\x97/g" -e "s/%98/\\x98/g" -e "s/%99/\\x99/g" -e "s/%9A/\\x9A/g" -e "s/%9B/\\x9B/g" -e "s/%9C/\\x9C/g" -e "s/%9D/\\x9D/g" -e "s/%9E/\\x9E/g" -e "s/%9F/\\x9F/g" -e "s/%A0/\\xA0/g" -e "s/%A1/\\xA1/g" -e "s/%A2/\\xA2/g" -e "s/%A3/\\xA3/g" -e "s/%A4/\\xA4/g" -e "s/%A5/\\xA5/g" -e "s/%A6/\\xA6/g" -e "s/%A7/\\xA7/g" -e "s/%A8/\\xA8/g" -e "s/%A9/\\xA9/g" -e "s/%AA/\\xAA/g" -e "s/%AB/\\xAB/g" -e "s/%AC/\\xAC/g" -e "s/%AD/\\xAD/g" -e "s/%AE/\\xAE/g" -e "s/%AF/\\xAF/g" -e "s/%B0/\\xB0/g" -e "s/%B1/\\xB1/g" -e "s/%B2/\\xB2/g" -e "s/%B3/\\xB3/g" -e "s/%B4/\\xB4/g" -e "s/%B5/\\xB5/g" -e "s/%B6/\\xB6/g" -e "s/%B7/\\xB7/g" -e "s/%B8/\\xB8/g" -e "s/%B9/\\xB9/g" -e "s/%BA/\\xBA/g" -e "s/%BB/\\xBB/g" -e "s/%BC/\\xBC/g" -e "s/%BD/\\xBD/g" -e "s/%BE/\\xBE/g" -e "s/%BF/\\xBF/g" -e "s/%C0/\\xC0/g" -e "s/%C1/\\xC1/g" -e "s/%C2/\\xC2/g" -e "s/%C3/\\xC3/g" -e "s/%C4/\\xC4/g" -e "s/%C5/\\xC5/g" -e "s/%C6/\\xC6/g" -e "s/%C7/\\xC7/g" -e "s/%C8/\\xC8/g" -e "s/%C9/\\xC9/g" -e "s/%CA/\\xCA/g" -e "s/%CB/\\xCB/g" -e "s/%CC/\\xCC/g" -e "s/%CD/\\xCD/g" -e "s/%CE/\\xCE/g" -e "s/%CF/\\xCF/g" -e "s/%D0/\\xD0/g" -e "s/%D1/\\xD1/g" -e "s/%D2/\\xD2/g" -e "s/%D3/\\xD3/g" -e "s/%D4/\\xD4/g" -e "s/%D5/\\xD5/g" -e "s/%D6/\\xD6/g" -e "s/%D7/\\xD7/g" -e "s/%D8/\\xD8/g" -e "s/%D9/\\xD9/g" -e "s/%DA/\\xDA/g" -e "s/%DB/\\xDB/g" -e "s/%DC/\\xDC/g" -e "s/%DD/\\xDD/g" -e "s/%DE/\\xDE/g" -e "s/%DF/\\xDF/g" -e "s/%E0/\\xE0/g" -e "s/%E1/\\xE1/g" -e "s/%E2/\\xE2/g" -e "s/%E3/\\xE3/g" -e "s/%E4/\\xE4/g" -e "s/%E5/\\xE5/g" -e "s/%E6/\\xE6/g" -e "s/%E7/\\xE7/g" -e "s/%E8/\\xE8/g" -e "s/%E9/\\xE9/g" -e "s/%EA/\\xEA/g" -e "s/%EB/\\xEB/g" -e "s/%EC/\\xEC/g" -e "s/%ED/\\xED/g" -e "s/%EE/\\xEE/g" -e "s/%EF/\\xEF/g" -e "s/%F0/\\xF0/g" -e "s/%F1/\\xF1/g" -e "s/%F2/\\xF2/g" -e "s/%F3/\\xF3/g" -e "s/%F4/\\xF4/g" -e "s/%F5/\\xF5/g" -e "s/%F6/\\xF6/g" -e "s/%F7/\\xF7/g" -e "s/%F8/\\xF8/g" -e "s/%F9/\\xF9/g" -e "s/%FA/\\xFA/g" -e "s/%FB/\\xFB/g" -e "s/%FC/\\xFC/g" -e "s/%FD/\\xFD/g" -e "s/%FE/\\xFE/g" -e "s/%FF/\\xFF/g" -e "s/&#39;/\\\'/g" -e "s/%5E/^/g"
}

unescape_textarea()
{
	if [ $kill_backq -eq 0 ]
	then
		unescape_input "$1" | sed -e "s/%0D%0A/\n/g"
	else
		unescape_input "$1" | sed -e "s/%0D%0A/\n/g" -e "s/\`\.\`/./g" -e "s/\`/ /g"
	fi
}

unescape_execute()
{
	unescape_input "$1" | sed -e "s/%0D%0A/ /g"
}

escape_html()
{
	echo "$1" | sed -e "s/&/&amp;/g" -e "s/\\\/\&#92;/g"
}

display() {
	case "$2" in
		0) echo "$1" >> $output_tmpf;;
		1) echo "<FONT COLOR=\"Red\">ERROR: $1</FONT>" >> $output_tmpf;;
		2) echo "<FONT COLOR=\"Green\">$1</FONT>" >> $output_tmpf;;
		3) echo "<FONT COLOR=\"Orange\">$1</FONT>" >> $output_tmpf;;
	esac
}

debug() {
	d_text=$(echo "$1" | od -vc)
	echo ="<BR>DEBUG:<BR>$d_text<BR>"  >> $output_tmpf;
	echo "$1" >> $BASE/log/debug.log
}

mysql_debug()
{
	echo "$1" >> $BASE/log/mysql_debug.log
}

connection_setup()
{
	coproc mysqlc { stdbuf -oL mysql -ANnfrvv -u "$user" -p"$password" -h "$host" "$default_db" 2>&1; } 
	autoinc_inc=$(mysql_query "SELECT variable_value FROM information_schema.global_variables WHERE variable_name = 'auto_increment_increment'")
	mysql_query "BEGIN" > /dev/null
	start_time=$(mysql_query "SELECT DATE_FORMAT(UTC_TIMESTAMP(), '%d-%m-%Y %H:%i:%S')")
	mysql_query "SET NAMES utf8" > /dev/null
	mysql_query "set session group_concat_max_len=4096" > /dev/null
}

mysql_query()
{
	rm -f $errors_tmpf
	thisquery="${1/# /}"
	skip=0
	error=0
	[ $speed_hacks -eq 0 ] && cq=$(echo ${thisquery,,} | iconv -c -f utf-8  | tr -d "\r\n\t") || cq=${thisquery,,}
	ncq=${cq#"${cq%%[![:space:]]*}"}
	qtype=${ncq/%\ */}
	if [ "$2" != "" -a "$2" != "$(cat $cached_db_tmpf 2>/dev/null)" ] 
	then
		echo "use $2;"  >&${mysqlc[1]}
		mysql_debug "($ticket)>use $2;"
		echo "$2" > $cached_db_tmpf
	fi
	echo "$thisquery;" >&${mysqlc[1]}
	mysql_debug "($ticket)>$thisquery;"
	while read -rt 15 -u ${mysqlc[0]} myrow
	do
		if [ "$myrow" = "--------------" ]
		then
			[ $skip -eq 0 ] && skip=1 || skip=0
			continue
		fi
		[ $skip -eq 1 ] && continue
		[ "$myrow" = "" ] && continue
		case "$qtype" in
			'use')
					echo "$myrow"
					mysql_debug "($ticket)<$myrow"
					[[ $myrow == *"Database changed"* ]] && break
					;;
			'update')
					echo "$myrow"
					mysql_debug "($ticket)<$myrow"
					[[ $myrow == *"Rows matched:"* ]] && break
					;;
			'select'|'show'|'explain')
					[[ $myrow == *"Empty set"* ]] && break
					[[ $myrow == *"row"*"in set"* ]] && break
					[[ $myrow == "ERROR "* ]] && break
					echo "$myrow"
					mysql_debug "($ticket)<$myrow"
					;;
			*)
					[[ $myrow == "ERROR "* ]] && break
					echo "$myrow"
					mysql_debug "($ticket)<$myrow"
					if [[ $myrow == *"row"*"affected"* ]]
					then 
						echo "$myrow" | cut -d " " -f 3 > $rows_tmpf
						break
					fi
					;;
		esac
		[[ $myrow == "ERROR "* ]] && break
	done
	if [[ $myrow == "ERROR "* ]]
	then
		mysql_debug "($ticket)<$myrow"
		echo "$myrow" > $errors_tmpf
		error=1
		return
	fi
	case "$qtype" in
		'begin'|'use'|'show'|'select'|'set'|'commit'|'rollback'|'create'|'explain')
			;;
		*)
			show_warnings > $w_resultset_tmpf
			grep -v ^Records $w_resultset_tmpf > $warnings_tmpf
			;;
	esac
}

show_warnings()
{
	skip=0
	echo "show warnings;" >&${mysqlc[1]}
	mysql_debug "($ticket)>show warnings;"
	while read -rt 15 -u ${mysqlc[0]} myrow
	do
		if [ "$myrow" = "--------------" ]
		then
			[ $skip -eq 0 ] && skip=1 || skip=0
			continue
		fi
		[ $skip -eq 1 ] && continue
		[ "$myrow" = "" ] && continue
		[[ $myrow == *"Empty set"* ]] && break
		[[ $myrow == *"row"*"in set"* ]] && break
		echo "$myrow"
		mysql_debug "($ticket)<$myrow"
	done
}

delete_rollback ()
{
	case $4 in
		0) insert="INSERT";;
		1) insert="REPLACE";;
	esac
	if [ "$1.$2" != "$dr_cache" ]
	then
		tc=$(mysql_query "SELECT GROUP_CONCAT('\`', column_name, '\`') FROM information_schema.columns  WHERE table_schema = '$1' AND table_name = '$2'")
		dr_cache="$1.$2"
	fi
	rtc=$(echo $tc | sed -e "s/,/,'\n', '@xc_NL@'), '\r', '@xc_CR@'), '\t', '@xc_TAB@'),REPLACE(REPLACE(REPLACE(/g" -e "s/^/REPLACE(REPLACE(REPLACE(/g" -e "s/$/,'\n', '@xc_NL@'), '\r', '@xc_CR@'), '\t', '@xc_TAB@')/g")
	mysql_query "SELECT $rtc FROM $1.$2 WHERE $3 /* delete_rollback */" > $dump_tmpf
	[ -s $dump_tmpf ] && cat  $dump_tmpf | sed -e "s/	/','/g" -e "s/^/$insert INTO $1.$2 VALUES ('/g" -e "s/$/');/g" -e "s/'NULL'/NULL/g" -e "s/@xc_NL@/\\\n/g" -e "s/@xc_CR@/\\\r/g" -e "s/@xc_TAB@/\\\t/g"
}

page_style()
{
	printf "<head>\n"
	printf "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/push.js/0.0.11/push.min.js\"></script>\n"
	printf "<link rel=\"icon\" type=\"image/png\" href=/favicon.png\"/>"
	printf "<style>\n"
	printf "body {\n"
    	printf "\tbackground-color: white;\n"
    	printf "\tcolor: maroon;\n"
	printf "\tfont-family: Arial, Helvetica, sans-serif;\n"
	printf "} \n"
	printf "#overlay {\n"
     	printf "\tvisibility: hidden;\n"
     	printf "\tposition: absolute;\n"
     	printf "\tleft: 0px;\n"
     	printf "\ttop: 0px;\n"
     	printf "\twidth:100%%;\n"
     	printf "\theight:100%%;\n"
     	printf "\tz-index: 1000;\n"
	printf "}\n"
	printf "#barcontainer{\n"
    	printf "\twidth:500px;\n"
     	printf "\tmargin: 100px auto;\n"
     	printf "\tbackground-color: #fff;\n"
    	printf "\theight:15px;\n"
    	printf "\tborder:1px solid #000;\n"
    	printf "\toverflow:hidden; \n"
	printf "}\n"
	printf "#progressbar{\n"
    	printf "\twidth:37%%;\n"
    	printf "\theight:15px;\n"
    	printf "\tborder-right: 1px solid #000000;\n"
    	printf "\tbackground: #d65946;\n"
	printf "}\n"
	printf "#percent {\n"
    	printf "\tcolor: black;\n"
    	printf "\ttext-align: center;\n"
    	printf "\tfont-size: 15px;\n"
    	printf "\tfont-style: italic;\n"
    	printf "\tfont-weight: bold;\n"
    	printf "\tleft: 25px;\n"
    	printf "\tposition: relative;\n"
    	printf "\ttop: -16px;\n"
	printf " }\n"
	printf ".baka12 {\n"
	printf "\tfont-family: Arial, Helvetica, sans-serif;\n"
    	printf "\tfont-size: 12px;\n"
	printf " }\n"
	printf ".baka14 {\n"
	printf "\tfont-family: Arial, Helvetica, sans-serif;\n"
    	printf "\tfont-size: 14px;\n"
	printf " }\n"
	printf ".baka20 {\n"
	printf "\tfont-family: Arial, Helvetica, sans-serif;\n"
    	printf "\tfont-size: 20px;\n"
	printf " }\n"
	printf ".c2cc {\n"
    	printf "\tcolor: darkcyan;\n"
    	printf "\tfont-size: 12px;\n"
	printf "\tfont-family: Arial, Helvetica, sans-serif;\n"
    	printf "\tfont-weight: bold;\n"
	printf " }\n"
	printf "</style>\n"
	printf "<TITLE>BakaSQL v%s</TITLE>\n" "$VERSION"
	printf "<script type=\"text/javascript\">\n"
	printf "function overlay() {\n"
	printf "\tel = document.getElementById(\"overlay\");\n"
	printf "\tel.style.visibility = (el.style.visibility == \"visible\") ? \"hidden\" : \"visible\";\n"
	printf "}\n"
	printf "function draw(max, pos){\n"
    	printf "\tvar percent=Math.round((pos*100)/max);\n"
    	printf "\tdocument.getElementById(\"progressbar\").style.width=percent+'%%';\n"
    	printf "\tdocument.getElementById(\"percent\").innerHTML='Progress: ' + percent+'%%';\n"
	printf "}\n"
	printf "function adv_options() {\n"
	printf "\tel = document.getElementById(\"adv\");\n"
	printf "\tel.style.display = (el.style.display == \"block\") ? \"none\" : \"block\";\n"
	printf "}\n"
	printf "</script>\n"
	printf "</head>\n"
}

clipboard_code()
{
	printf "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/1.5.5/clipboard.min.js\"></script>\n"
	printf "<script type=\"text/javascript\">\n"
	printf "new Clipboard('.c2cc');\n"
	printf "</script>\n"
}

show_form()
{
	printf "<TABLE><TR>"
	if [ $post -eq 1 -a $post_error -eq 0 -a $total_errors -eq 0 ]
	then
		printf "<TD ROWSPAN=3 VALIGN=TOP><IMG HEIGHT=50 SRC=\"/bb.png\"></TD><TD>&nbsp;</TD>"
		printf "</TR><TR>"
		printf "<TD ROWSPAN=2><IMG HEIGHT=80 BORDER=0 SRC=\"/bakasql.png\"></TD>"
	else
		printf "<TD ROWSPAN=2><IMG HEIGHT=80 BORDER=0 SRC=\"/bakasql.png\"></TD>"
		printf "<TD CLASS=\"baka20\"><B>BakaSQL</B><BR>"
		printf	"<SPAN CLASS=\"baka14\">Eating SQL for a living&trade;</SPAN></TD>"
		printf "</TR><TR>"
		printf	"<TD CLASS=\"baka12\">version: $VERSION</TD>"
	fi
	printf "</TR></TABLE>"
	printf "<BR>"
	printf "<FORM METHOD=\"POST\" ACTION=\"$SCRIPT_NAME\" accept-charset=\"UTF-8\">\n"
	printf "<TABLE>\n"
	printf "<TR><TD>Host:</TD>"
	printf "<TD><SELECT NAME=\"host\" SIZE=1>"
	IFS="
"
	for ho in $(cat $HOSTFILE)
	do
		[ "$ho" = "$host" ] && printf "<OPTION SELECTED>$ho\n" || printf "<OPTION>$ho\n"
	done
	printf "</SELECT></TD></TR>\n"
	printf "<TR><TD>User:</TD><TD><INPUT TYPE=TEXT NAME=\"user\" VALUE=\"$user\" MAXLENGTH=16 SIZE=16></TD></TR>\n"
	printf "<TR><TD>Password:</TD><TD><INPUT TYPE=PASSWORD NAME=\"password\" VALUE=\"$password\" MAXLENGTH=40 SIZE=16></TD></TR>\n"
	printf "<TR><TD>Schema:</TD><TD><INPUT TYPE=TEXT NAME=\"schema\" VALUE=\"$default_db\" MAXLENGTH=64 SIZE=32></TD></TR>\n"
	printf "<TR><TD>Ticket #:</TD><TD><INPUT TYPE=TEXT NAME=\"ticket\" VALUE=\"$ticket\" MAXLENGTH=16 SIZE=16></TD></TR>\n"
	printf "<TR><TD>Remove backquotes:</TD><TD><INPUT TYPE=CHECKBOX NAME=\"backq\"></TD></TR>\n" 
	printf "<TR><TD COLSPAN=2><FONT SIZE=1><A HREF=\"#\" onclick=\"adv_options();\">advanced options</A></FONT></TD><TR>\n"
	printf "<TR><TD COLSPAN=2>\n"
	printf "<DIV ID=\"adv\" STYLE=\"display:none\">\n"
	printf "<FONT SIZE=2><BR>WARNING: do not use these features unless you know how they work!<BR>\n"
	printf "Enable speed hacks: &nbsp;<INPUT TYPE=CHECKBOX NAME=\"hacks\"><BR>\n" 
	printf "Enable periodic commit: &nbsp;<INPUT TYPE=CHECKBOX NAME=\"commit\"><BR>\n" 
	printf "Commit interval: &nbsp;<INPUT TYPE=TEXT NAME=\"commit_intv\" MAXLENGTH=5 SIZE=5 VALUE=\"$commit_interval\">\n" 
	printf "</FONT><BR><BR>\n"
	printf "</DIV>\n"
	printf "</TD></TR>\n"
	[ $dryrun -eq 1 ] && textarea=$(escape_html "$(unescape_textarea $query)")
	printf "<TR><TD COLSPAN=2><TEXTAREA NAME=\"query\" ROWS=8 COLS=200>%s</TEXTAREA></TD></TR>\n" "$textarea"
	printf "<TR><TD COLSPAN=2>&nbsp;</TD></TR>\n"
	printf "<TR><TD COLSPAN=2><B><PRE>%s</PRE></B></TD></TR>\n" "$(cat $output_tmpf 2>/dev/null)"
	printf "<TR><TD COLSPAN=2>&nbsp;</TD></TR>\n"
	[ $dryrun -eq 1 ] && checkbox="CHECKED"
	printf "<TR><TD>Dry Run:</TD><TD ALIGN=LEFT><INPUT TYPE=CHECKBOX NAME=\"dryrun\" VALUE=\"on\" %s></TD></TR>\n" "$checkbox"
	[ $enable_ninja -eq 1 ] && printf "<TR><TD>Enable <I>Ninja Mode</I> (BE CAREFUL!! Make sure you know what you are doing before enabling this!)</TD><TD ALIGN=LEFT><INPUT TYPE=CHECKBOX NAME=\"ninja\" VALUE=\"on\"></TD></TR>\n" 
	printf "<TR><TD COLSPAN=2>&nbsp;</TD></TR>\n"
	printf "<TR><TD COLSPAN=2><INPUT TYPE=\"SUBMIT\" VALUE=\"Execute\">\n"
	printf "</TABLE>\n"
	printf "</FORM>\n"
	clipboard_code
}

log()
{
	ts=$(date "+%Y-%m-%d %T")
	printf "%s %-10s %-16s %-10s %-20s %s\n" "$ts" "$ticket" "$user" "$host" "$db" "$1" >> $BASE/log/execution.log
}

post_checks()
{
	post_error=0
	echo "x" > $BASE/log/.fscheck
	x=$(cat $BASE/log/.fscheck)
	if [ "$x" != "x" ] 
	then
		display "FILE SYSTEM FULL, cannot operate" 1
		post_error=1
		return
	fi
	if [ "$host" = "" ] 
	then 
		display "Please specify a server" 1
		post_error=1
		return
	fi
	if [ "$user" = "" ]
	then
		display "Please specify your user" 1
		post_error=1
		return
	fi
	if [ "$user" = "root" ]
	then
		display "Root access is not allowed" 1
		post_error=1
		return
	fi
	if [ "$password" = "" ]
	then
		display "Please specify your password" 1
		post_error=1
		return
	fi
	password=$(unescape_input "$password")
	err=$(mysqladmin -u "$user" -p"$password" -h"$host" ping 2>&1 | fgrep error | cut -d":" -f2-)
	if [ "$err" != "" ]
	then
		display "$err" 1
		post_error=1
		return
	fi
	if [ "$(echo "show variables like 'read_only'" | mysql -ANr -u "$user" -p"$password" -h"$host" 2>&1 | cut -f 2)" != "OFF" ]
	then
		display "This instance is READ ONLY" 1
		post_error=1
		return
	fi
	if [ "$ticket" = "" ]
	then
		display "Ticket ID cannot be empty" 1
		post_error=1
	fi
	if [ "$(echo $ticket | tr -d  "[:alnum:]-_")" != "" ]
	then
		display "Ticket ID can only contain numbers, letters and the dash character" 1
		post_error=1
	fi
	if [ "$default_db" != "" ]
	then
		res=$(mysql -u "$user" -p"$password" -h"$host" "$default_db" 2>&1)
		if [ "$res" != "" ]
		then
			display "$res" 1
			post_error=1
		fi
	fi
}

run_statement()
{
	error=0
	mysql_query "$1" "$db" > $resultset_tmpf
	result=$(cat $resultset_tmpf)
	warning_text=$(cat $warnings_tmpf 2>/dev/null)
	error_text=$(cat $errors_tmpf 2>/dev/null)
	[ "$warning_text" != "" ] && total_warnings=$((total_warnings+1))
	if [ "$error_text" != "" ]
	then
		error=1
		total_errors=$((total_errors+1))
	fi
	if [ $error -eq 1 ]
	then
		case $2 in
			0)
				display "$error_text" 1
				;;
			1) 	
				display "<BR>DRY RUN RESULT: $error_text" 1
				;;
				
		esac
	else
		case ${q[0],,} in
			'insert'|'replace') 
				if [ $auto_increment -eq 1 ]
				then
 					mysql_query "SELECT LAST_INSERT_ID()" > $resultset_tmpf
 					q_last_id=$(cat $resultset_tmpf)
				else
					q_last_id=0
				fi
				;;
			*)
				q_last_id=0
				;;
		esac	
		last_id=$q_last_id
		case $2 in
			0)	display "$result" 2
				display "$warnings" 3
				log "$1"
				;;
			1) 	display "<BR>DRY RUN RESULT:<BR>$result<BR>$warning_text" 3
				;;
		esac
	fi
}

array_idx()
{
	$BAKAUTILS array_idx "$1" "$2"  2>>/tmp/bakautils.log
}

check_key()
{
	c=0
	a=("$1")
	for arg in ${a[@]}
	do
		display "$c $arg" 0
		c=$((c + 1))
	done
}

num_rows()
{
	[ "$nr_cache" = "$db.$table" ] && return
	rows=$(mysql_query  "SELECT TABLE_ROWS FROM information_schema.tables WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table'")
	nr_cache="$db.$table"
}

autoinc_rollback()
{
	get_pk $db $table
	for idx in $(seq -s "	" 1 1 $rows_affected)
	do
		case $dryrun in 
			0) 	[ $idx -eq 1 ] && echo "DELETE FROM $db.$table WHERE $pk = '$last_id';" || echo "DELETE FROM $db.$table WHERE $pk = '$((last_id + (idx - 1) * autoinc_inc))';"
				;;
			1) 
				[ $idx -eq 1 ] && echo "DELETE FROM $db.$table WHERE $pk = 'ASSIGNED AUTOINC VALUE';" || echo "DELETE FROM $db.$table WHERE $pk = 'ASSIGNED AUTOINC VALUE + $(((idx - 1) * autoinc_inc))';"
				;;
		esac
	done
}

get_col_names()
{
	case "$2" in
		0) 	rr_col_names=($(echo "$1" | cut -d "(" -f 2 | cut -d ")" -f 1 | sed -e "s/,/, /g" | tr -d ","))
			rr_q="$1"
			;;
		1) 	
			if [ "$rr_cache1" != "$db.$table" ] 
			then
				rr_col_names_c=$(mysql_query "SELECT GROUP_CONCAT(COLUMN_NAME) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table'") 
				rr_col_names=($(echo $rr_col_names_c | tr "," " "))
				rr_cache1="$db.$table"
			fi
			rr_q=$(echo "$1" | sed -e "s/VALUES/($rr_col_names_c) values/gi")
			;;
	esac
}

replace_rollback()
{
	saveIFS="$IFS"
	if [ "$rr_cache2" != "$db.$table" ]
	then
		rr_unique=$(mysql_query "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND CONSTRAINT_TYPE='UNIQUE' LIMIT 1")
		if [ "$rr_unique" != "" ]
		then
			rs=$(mysql_query "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE CONSTRAINT_NAME = '$rr_unique' AND TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table'")
			rr_ukeys=($(echo "$rs" | tr "\n" " "))
		else
			unset rr_ukeys
		fi
		rs=$(mysql_query "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE CONSTRAINT_NAME = 'PRIMARY' AND TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table'")
		rr_keys=($(echo "$rs" | tr "\n" " "))
		if [ "$rr_keys" = "" -a "$rr_unique" = "" ]
		then
			echo "-- The table lacks an unique index. Rollback is not possible."
			return
		fi
		IFS="	"
		rr_nkeys=${#rr_keys[@]}
		rr_nukeys=${#rr_ukeys[@]}
		rr_nkeys_used=0
		rr_nukeys_used=0
		for arg in ${rr_col_names[@]}
		do
			nobq="${arg//\`}"
			for arg2 in ${rr_keys[@]} 
			do
				[ "${nobq,,}" = "${arg2,,}" ] && rr_nkeys_used=$((rr_nkeys_used + 1))
			done
			for arg2 in ${rr_ukeys[@]} 
			do
				[ "${nobq,,}" = "${arg2,,}" ] && rr_nukeys_used=$((rr_nukeys_used + 1))
			done
		done
		rr_cache2="$db.$table"
	fi
	echo "-- Rollback instructions for query $qc"
	if [ $rr_nkeys != $rr_nkeys_used -a $auto_increment -eq 0 ]
	then
		if [ "$rr_unique" = "" ]
		then
			echo "-- $2 is not using primary key fully (cols needed $rr_nkeys, used $rr_nkeys_used). Rollback not possible"
			IFS="$saveIFS"
			return
		else
			if [ $rr_nukeys != $rr_nukeys_used ]
			then
				echo "-- $2 is not using unique index fully (cols needed $rr_nukeys, used $rr_nukeys_used). Rollback not possible"
				IFS="$saveIFS"
				return
			fi
		fi
	fi
	rr_using_primary=0
	[ $rr_nkeys -eq $rr_nkeys_used ] && rr_using_primary=1
	[ $auto_increment -eq 1  ] && rr_using_primary=1
	# if both primary key and unique index are available, prefer unique index for rollback
	if [ $rr_nukeys -gt 0 -a $rr_nukeys -eq $rr_nukeys_used ]
	then
		has_both=1
		rr_using_primary=0
	else
		has_both=0
	fi
	#echo "-- DEBUG: keys=$rr_nkeys used=$rr_nkeys_used ukeys=$rr_nukeys used=$rr_nukeys_used using_primary=$rr_using_primary"
	# special case: autoinc pk and no unique index
	if [ $replace -eq 0 -a $rr_using_primary -eq 1 -a $auto_increment -eq 1 ]
	then
		IFS="	"
		autoinc_rollback
		IFS="$saveIFS"
		return
	fi
	IFS="
"
	for rr_row in $(echo "$rr_q" | cut -d ")" -f2- | sed -e "s/ *VALUES *//ig" -e "s/ *VALUES *(/(/ig" -e "s/ *VALUES$//ig" -e "s/),(/\x0a/g"  -e "s/^ *(//g"  -e "s/), *(/\x0a/g" -e "s/) *, *(/\x0a/g" -e "s/) *;*$//g" -e "s/' *, */'	/g" -e "s/ *, */	/g")
	do
		IFS="	"
		rr_col_values=($rr_row)
		rr_idx=0
		rr_kc=0
		rr_where=""
		undet=0
		while true
		do
			[ $rr_idx -eq ${#rr_col_names[@]} ] && break
			case $rr_using_primary in
				0)
					for arg in ${rr_ukeys[@]} 
					do
						nobq="${rr_col_names[$rr_idx]//\`}"
						if [ "${nobq,,}" = "${arg,,}" ]
						then
							if [ "$(echo ${rr_col_values[$rr_idx]} | grep -v "^'" | tr -dc '()')" != "" ]
							then
								undet=1	# insert contains non deterministic values
								break
							fi
							[ $rr_kc -gt 0 ] && rr_where="$rr_where AND"
							rr_where="$rr_where ${rr_col_names[$rr_idx]} = ${rr_col_values[$rr_idx]}"
							rr_kc=$((rr_kc + 1))
						fi
					done
					;;
				1)
					for arg in ${rr_keys[@]} 
					do
						nobq="${rr_col_names[$rr_idx]//\`}"
						if [ "${nobq,,}" = "${arg,,}" ]
						then
							[ $rr_kc -gt 0 ] && rr_where="$rr_where AND"
							rr_where="$rr_where ${rr_col_names[$rr_idx]} = ${rr_col_values[$rr_idx]}"
							rr_kc=$((rr_kc + 1))
						fi
					done
					;;
			esac
			[ $undet -eq 1 ] && break
			rr_idx=$((rr_idx + 1))
		done
		[ $undet -eq 1 ] && break
		echo "DELETE FROM $db.$table WHERE $rr_where;"
		
		[ $replace -eq 1 ] && delete_rollback  "$db" "$table" "$rr_where" 0
		IFS="
"
	done
	if [ $undet -eq 1 ]
	then
		if [ $has_both -eq 1 -a $replace -eq 0 -a $auto_increment -eq 1 ]
		then
			IFS="	"
			echo "-- NOTICE: using PK for rollback due to non deterministic values in INSERT statement"
			autoinc_rollback
		else
			echo "-- WARNING! undeterministic values in INSERT statement, rollback not possible"
		fi
	fi
	IFS="$saveIFS"
}

get_pk()
{
	[ "$pk_cache" = "$1.$2" ] && return
	rs=$(mysql_query "SHOW INDEX FROM $1.$2 WHERE KEY_NAME = 'PRIMARY'" "$1")
	pk=$(echo "$rs" | cut -f 5 | tr "\n" " " | sed -e "s/ $//g")
	pk_cache="$1.$2"
}
			
check_autoincrement()
{
	[ "$ai_cache" = "$db.$table" ] && return
	auto_increment=$(mysql_query "SELECT IF(COUNT(*) = 1, 1, 0) FROM information_schema.columns WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND EXTRA = 'auto_increment'")
	ai_cache="$db.$table"
}

autoincrement_name()
{
	[ "$ain_cache" = "$db.$table" ] && return
	ai_col_name=$(mysql_query "SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND EXTRA = 'auto_increment'")
	ain_cache="$db.$table"
}
			
index_name()
{
	[ "$in_cache" = "$db.$table.$1" ] && return
	idxname=$(mysql_query "SELECT INDEX_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND COLUMN_NAME = '$1'")
	in_cache="$db.$table.$1"
}

index_parts()
{
	[ "$ip_cache" = "$db.$table.$1" ] && return
	idxcount=$(mysql_query "SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND INDEX_NAME = '$1'")
	ip_cache="$db.$table.$1"
}

check_pk_use()
{
	pk_in_use=$($BAKAUTILS check_pk_use "$1" "$pk"  2>>/tmp/bakautils.log)
}

check_table_presence()
{
	table_present=1
	if [ $(echo $table | fgrep -c "." ) -eq 0 ]
	then
		if [ "$default_db" = "" ]
		then
			display "Default schema not set" 1
			table_present=0
			return
		else
			db=$default_db
		fi
	else
		st=$table	
		db=$(echo $st | cut -d"." -f 1)
		table=$(echo $st | cut -d"." -f 2)
	fi
	[ "$ctp_cache" = "$db.$table" ] && return
	there=$(mysql_query "SELECT COUNT(*) FROM information_schema.tables WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME= '$table'")
	if [ $there -eq 0 ]
	then
		display "No table named \"$table\" in schema \"$db\"" 1
		table_present=0
		return
	else
		ctp_cache="$db.$table"
	fi
}

check_columns()
{
	[ "$cc_cache" = "$db.$table.$1" ] && return
	columns_ok=1
	for arg in $1
	do
		[ $(echo $arg | fgrep -c ".") -gt 0 ] && arg=$(echo $arg | cut -d"." -f 2)
		arg=$(echo $arg | tr -d "\`")
		cc=$(mysql_query "SELECT COUNT(*) + IF (COLUMN_KEY = 'PRI', 1, 0) FROM information_schema.columns WHERE TABLE_SCHEMA = '$db' AND TABLE_NAME = '$table' AND COLUMN_NAME = '$arg' /* check_columns */")
		case $cc in
			0)
				display "Column \"$arg\" does not exist" 1
				columns_ok=0
				return
				;;
			2)
				display "Sorry, BakaSQL cannot update column \"$arg\" because is (part of) a primary key and rollback would be incorrect" 1
				columns_ok=0
				cc_cache=""
				return
				;;
		esac
	done
	cc_cache="$db.$table.$1"
}

rollback_args()
{
	$BAKAUTILS rollback_args "$1" 2>>/tmp/bakautils.log
}

rollback_pkwhere()
{
	echo -n "CONCAT("
	c=0
	for arg in $1
	do
		[ $c -gt 0 ] && echo -n ",' AND ',"
		echo -n "'$arg=\'',\`$arg\`,'\''"
		c=$(($c + 1))
	done
	echo ")"
}

verify_column_names()
{
	columns_check=1
	if [ "$2.$3" != "$vcn_cache" ]
	then
		vcn_tc=$(mysql_query "SELECT GROUP_CONCAT(COLUMN_NAME SEPARATOR ' ') FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '$2' AND TABLE_NAME = '$3'")
		vcn_cache="$2.$3"
	fi
	cl=$($BAKAUTILS verify_column_names "$1" "$vcn_tc" 2>>/tmp/bakautils.log)
	if [ $? -eq 1 ]
	then 
		display "column $cl does not exist" 1
		columns_check=0
	fi
}

index_in_use()
{
	if [ "$2" = "" ] 
	then
		local ldb=$db
		local ltable=$table
	else
		local ldb=$2
		local ltable=$3
	fi
	verify_column_names "$1" $ldb $ltable
	if [ $columns_check -eq 0 ]
	then 
		using_index=0
		return
	fi
	using_index=0
	if [ "$ldb.$ltable" != "$iiu_cache" ]
	then
		mysql_query "SELECT s.column_name, s.seq_in_index,  ROUND(s.cardinality / t.table_rows * 100) AS card, s.index_name, (SELECT COUNT(*) FROM information_schema.STATISTICS WHERE table_schema =  '$ldb' AND table_name = '$ltable' AND index_name=s.index_name) AS size FROM information_schema.STATISTICS s LEFT JOIN information_schema.TABLES t ON s.table_schema = t.table_schema AND s.table_name = t.table_name  WHERE s.table_schema =  '$ldb' AND s.table_name = '$ltable' ORDER BY s.index_name, s.seq_in_index" > $cardinfo_tmpf
		iiu_cache="$ldb.$ltable"
	fi
	cardmsg=$($BAKAUTILS index_in_use $cardinfo_tmpf "$cl" $MIN_REQ_CARDINALITY 2>>/tmp/bakautils.log)
	if [ $? -eq 0 ]
	then
		using_index=1
		enable_ninja=0
		return
	fi
	if [ "$cardmsg" != "" ]
	then
		if [ $ninja -eq 0 ]
		then
			enable_ninja=1
			display "$cardmsg" 3
		else
			display "WARNING: Considering low cardinality index due to <I>ninja mode</I> being enabled. Good luck." 3
			using_index=1
		fi
	fi
	return
}

insert_vars()
{
	qte=$($BAKAUTILS insert_vars $vars_tmpf "$1" $last_id 2>>/tmp/bakautils.log)
}

query_set()
{
	total_errors=$((total_errors+1))
	n=$(echo "$1" | sed -e "s/=/ = /" -e "s/(/ (/")	
	IFS=" " q=($n)
	i=0
	vval=""
	for arg in ${q[@]}
	do
		case $i in
			0) 
				;;
			1) 	if [[ $arg != "@"* ]]
				then
					display "syntax error near \"$arg\"" 1
					return
				fi
				if [[ $arg = *":"* ]]
				then
					display "syntax error near \"$arg\"" 1
					return
				fi
				vname=$(echo $arg | cut -d"@" -f 2)
				;;
			2) 	if [ "$arg" != "=" ]
				then
					display "syntax error near \"$arg\"" 1
					return
				fi
				;;
			*)	if [[ ${arg,,} = *"last_insert_id()"* ]]
				then
					display "not supported, use automatic variable @last_insert_id instead" 1
					return
				fi
				if [[ ${arg,,} = *"join"* ]]
				then
					display "JOIN not supported in variable assignment" 1
					return
				fi
				vval="$vval$arg "
				;;
		esac
		i=$((i+1))
	done
	if [ $(cat $vars_tmpf 2>/dev/null | cut -f 1  | fgrep -c $vname) -ne 0 ]
	then
		display "duplicate variable assignment" 1
		return
	fi
	eok=0
	if [[ "$vval" == "("* ]]
	then
		if [[ "${vval}" == *") " ]] 
		then
			eok=1
		fi
	fi
	if [ $eok -eq 0 ]
	then
		display "variable expression must be enclosed within \"(\" and \")\"" 1
		return
	fi
	vval=$(echo "$vval" | sed -e "s/^(//" -e "s/)$//" -e "s/)[; ]*$//")
	IFS=" " q=($vval)
	if [ ${q[0],,} != "select" ]
	then
		display "only SELECT accepted as variable expression at this time" 1
		return
	fi
	i=0
	w=0
	for arg in ${q[@]}
	do
		if [ "${arg,,}" = "from" ]
		then
			w=$((i+1))
			break
		fi
		i=$((i + 1))
	done
	if [ $w -ge 1 ]
	then
		vfrom=${q[$w]}
		vdb=$(echo $vfrom | cut -d "." -f 1)
		vtable=$(echo $vfrom | cut -d "." -f 2)
		if [ "$vdb" = "$vtable" ]
		then
			if [ "$default_db" != "" ]
			then
				vdb=$default_db
			else
				display "table spec in variable expression is missing and default schema is not set" 1
				return
			fi
		fi
		i=0
		w=0
		for arg in ${q[@]}
		do
			if [ "${arg,,}" = "where" ]
			then
				w=$i
				break
			fi
			i=$((i + 1))
		done
		if [ $w -eq 0 ]
		then
			display "missing WHERE condition in variable expression" 1
			return
		fi
		vcond=""
		i=0
		for arg in ${q[@]}
		do
			if [ $i -gt $w ]
			then
				vcond="$vcond$arg "
			fi
			i=$((i + 1))
		done
		index_in_use "$vcond" $vdb $vtable
		[ $columns_check -eq 0 ] && return
		if [ $using_index -eq 0 ]
		then
			display "variable expression not using an index" 1
			return
		fi
		vcheck=""
		i=0
		for arg in ${q[@]}
		do
			case $i in
				1) vcheck="${vcheck}count(*) ";;
				*) vcheck="${vcheck}$arg ";;
			esac
			i=$((i+1))
		done
		insert_vars "$vcheck"
		vrows=$(mysql_query "$qte")
	else
		insert_vars "$vval"
		qres=$(mysql_query "$qte")
		if [ "$qres" = "" ]
		then
			display "expression returns no value" 1
			return
		fi
		if [ "$qres" = "NULL" ]
		then
			display "expression returns a NULL value" 1
			return
		fi
		vrows=$(echo "$qres" | wc -l)
	fi
	case "$vrows" in
		'0')
			display "expression returns no rows" 1
			return
			;;
		'1')
			
			;;
		'')
			
			display "$(cat $errors_tmpf 2>/dev/null)" 1
			return
			;;
		*)
			display "expression returns more than one row" 1
			return
			;;
	esac
	insert_vars "$vval"
	vres=$(mysql_query "$qte")
	display "Variable value assigned: @$vname = '$vres'" 3
	echo -e "$vname\t$vres" >> $vars_tmpf
	total_errors=$((total_errors-1))
}

query_delete()
{
	total_errors=$((total_errors+1))
	display "Query type: DELETE" 0
	IFS=" " q=($1)
	query_id=$2
	if [ "${q[1],,}" != 'from'  ]
	then
		display "Syntax error near \"${q[1]}\"" 1
		return
	fi
	table="${q[2]}"
	check_table_presence
	[ $table_present -ne 1 ] && return
	c=0
	w=0
	dml=""
	for arg in ${q[@]}
	do
		if [ $c -ge 3 ]
		then
			if [ "${arg,,}" = "where" ]
			then
				w=$c
				break
			fi
			dml="$dml$arg"
		fi
		c=$(($c + 1))
	done
	if [ $w -eq 0 ]
	then
		display "DELETE without WHERE is not allowed" 1
		return
	fi
	c=0
	where=""
	for arg in ${q[@]}
	do
		if [ $c -gt $w ]
		then
			where="$where $arg"
		fi
		c=$(($c + 1))
	done
	display "Schema: $db" 0
	display "Table: $table" 0
	whd=$(pretty_print "$where")
	display "WHERE condition: \"$whd\"" 0
	if [ $(array_idx "$where" "&&") -ge 0 ]
	then
		display "'&&' operator is not supported, please use 'AND'" 1
		return
	fi
	if [ $(array_idx "$where" "||") -ge 0 ]
	then
		display "'||' operator is not supported, please use 'OR'" 1
		return
	fi
	if [ $(array_idx "$where" "or") -ge 0 ]
	then
		display "OR condition in WHERE is not supported" 1
		return
	fi
	if [ $(array_idx "$where" ">") -ge 0 ]
	then
		display "\"greater than\" condition in WHERE is not supported" 1
		return
	fi
	if [ $(array_idx "$where" "<") -ge 0 ]
	then
		display "\"less than\" condition in WHERE is not supported" 1
		return
	fi
	explain_query
	[ $explain_check -eq 1 ] && return
	index_in_use "$where"
	[ $columns_check -eq 0 ] && return
	if [ $using_index -eq 0 -a $ninja -eq 0 ]
	then
		num_rows
		if [ $rows -ge 100000 ]
		then
			display "WHERE condition not using an index and table is large, query cannot be executed" 1
			return
		fi
	fi
	echo "-- Rollback instructions for query $qc" >> $rollback_file
	if [ $(echo $table | fgrep -c "." ) -ne 0 ]
	then
		parsed_db=$(echo $table | cut -d"." -f 1)	
		parsed_table=$(echo $table | cut -d"." -f 2)	
		delete_rollback  "$parsed_db" "$parsed_table" "$where" 0 > $tmpf
	else
		delete_rollback  "$db" "$table" "$where" 0 > $tmpf
	fi
	[ -s $tmpf ] && cat $tmpf >> $rollback_file
	total_errors=$((total_errors-1))
	run_statement "$1" $dryrun
}

explain_query()
{
	explain_check=0
	mysql_query "EXPLAIN SELECT * FROM $table WHERE $where" "$db" > $explain_tmpf
	er=($(cat $explain_tmpf | head -1 | tr "\t" " "))
	[ "${er[9]}" = "Impossible" ] && return
	[ "${er[11]}" = "no" -a "${er[12]}" = "matching" ] && return # 5.7
	if [ "${er[6]}" = "NULL" ]
	then
		num_rows
		if [ $rows -ge 10000 ]
		then
			display "WHERE condition not using an index, query cannot be executed" 1
			explain_check=1
		fi
	fi
}

query_insert()
{
	total_errors=$((total_errors+1))
	display "Query type: ${3^^}" 0
	[ "${3,,}" = "replace" ] && replace=1 || replace=0
	IFS=" " q=($(echo $1 | sed -e "s/(/ (/ig"))
	query_id=$2
	if [ "${q[1],,}" != "into" ]
	then
		display "Syntax error near \"${q[1]}\"" 1
		return
	fi
	table="${q[2]}"
	[ "${q[3],,}" = "values" ] && nocols=1 || nocols=0
	if [[ " ${q[@],,} " =~ " select " ]]; then
		if [[ ! " ${q[@],,} " =~ " values " ]]; then
			if [[ " ${q[@],,} " =~ " from " ]]; then
				if [ $ninja -eq 0 ]
				then
					display "${3^^}... SELECT is a dangerous contruct and should be avoided! Enable <I>ninja mode</I> to use it regardless." 1
					enable_ninja=1
					return
				fi
			fi
		fi
	fi
	echo $table | fgrep -q "(" && table=$(echo $table | cut -d "(" -f 1)
	check_table_presence
	[ $table_present -ne 1 ] && return
	check_autoincrement
	get_col_names "$1" $nocols
	display "Schema: $db" 0
	display "Table: $table" 0
	case $replace in
		0) 
			run_statement "$1" $dryrun
			if [ $error -eq 0 -a $auto_increment -eq 1 ]
			then
				[ "$last_aitable" != "$db.$table" ] && last_last_id=0
				if [ $last_id -eq $last_last_id ]
				then
					display "cannot insert a value in an AUTO_INCREMENT column" 1
					return
				fi
			fi
			rows_affected=$(cat $rows_tmpf)
			[ $error -eq 0 ] && replace_rollback "$1" "${3,,}" $nocols >> $rollback_file
			;;
		1)
			# if using REPLACE, rollback code needs to be executed before the actual statement
			replace_rollback "$1" "${3,,}" $nocols >> $rollback_file
			run_statement "$1" $dryrun
			;;
	esac
	total_errors=$((total_errors-1))
	if [ $dryrun -eq 0 -a $replace -eq 0 -a $auto_increment -eq 1 -a $error -eq 0 ] 
	then
		[ $rows_affected -eq 1 ] && display "AUTO-INC value assigned:  $last_id" 3 || display "AUTO-INC values assigned:  $last_id to $((last_id + rows_affected * autoinc_inc - autoinc_inc))" 3
	fi
	last_last_id=$last_id
	last_aitable=$db.$table
}

get_columns()
{
	cols=$($BAKAUTILS get_columns "$1" 2>>/tmp/bakautils.log)
}

query_update()
{
	fgp=$(echo "$1" | sed -E  -e "s/^ +//g" -e ':l' -e "s/^(.*)'([^a])*'(.*)$/\1?\3/g" -e "s/= ?[0-9]+/= '?'/g" -e 't l')
	[ $total_errors -eq 0 -a "$fgp" = "$update_old_fgp" ] && skip_checks=1 || skip_checks=0
	total_errors=$((total_errors+1))
	[ $speed_hacks -eq 0 ] && display "Query type: UPDATE" 0
	IFS=" " q=($1)
	query_id=$2
	if [ $skip_checks -eq 0 ]
	then
		if [ "${q[2],,}" != "set" ]
		then
			display "Syntax error near \"${q[2]}\"" 1
			return
		fi
		table="${q[1]}"
		check_table_presence
		[ $table_present -ne 1 ] && return
	fi
	qon=0
	c=0
	w=0
	dml=""
	for arg in ${q[@]}
	do
		uq1=${arg//\\\'}
		uq2=${uq1//[^\']}
		if [ $((${#uq2} % 2)) -eq 1 ]
		then
			[ $qon -eq 0 ] && qon=1 || qon=0
			[ $c -ge 3 ] && dml="$dml $arg"
			c=$((c + 1))
			continue
		fi
		if [ $qon -eq 0 ]
		then
			case "${arg,,}" in
				'where')
					w=$((c+1))
					break
					;;
				'and') 
					display "Syntax error near \"$arg\"" 1
					return
					;;
			esac
		fi
		[ $c -ge 3 ] && dml="$dml $arg"
		c=$((c + 1))
	done
	if [ $w -eq 0 ]
	then
		display "UPDATE without WHERE is not allowed" 1
		return
	fi
	c=0
	wn=$((${#q[@]}-1))
	where=${q[@]:$w:$((${#q[@]}-1))}
	if [ $skip_checks -eq 0 ]
	then
		get_columns "$dml"
		check_columns "$cols"
		[ $columns_ok -eq 0 ] && return
	fi
	if [ $speed_hacks -eq 0 ]
	then
		display "Schema: $db" 0
		display "Table: $table" 0
		d_text=$(escape_html "$dml")
		whd=$(pretty_print "$d_text")
		display "Set: $whd" 0
		whd=$(pretty_print "$where")
		display "WHERE condition: \"$whd\"" 0
	fi
	if [ $skip_checks -eq 0 ]
	then
		if [ $(array_idx "$where" "&&") -ge 0 ]
		then
			display "'&&' operator is not supported, please use 'AND'" 1
			return
		fi
		if [ $(array_idx "$where" "||") -ge 0 ]
		then
			display "'||' operator is not supported, please use 'OR'" 1
			return
		fi
		if [ $(array_idx "$where" "or") -ge 0 ]
		then
			display "OR condition in WHERE is not supported" 1
			return
		fi
		if [ $(array_idx "$where" ">") -ge 0 ]
		then
			display "\"greater than\" condition in WHERE is not supported" 1
			return
		fi
		if [ $(array_idx "$where" "<") -ge 0 ]
		then
			display "\"less than\" condition in WHERE is not supported" 1
			return
		fi
		notsrch=$(array_idx "$where" "not")
		if [ $notsrch -ge 0 ]
		then
			nullsrch=$(array_idx "$where" "null")
			nullsrch=$((nullsrch - 1))
			if [ $nullsrch -ne $notsrch ]
			then
				display "NOT condition in WHERE is not supported as indexes would not be used" 1
				return
			fi
		fi
		explain_query
		[ $explain_check -eq 1 ] && return
		index_in_use "$where"
		[ $columns_check -eq 0 ] && return
		if [ $using_index -eq 0 ]
		then
			display "BakaSQL couldn't find any usable index to satisfy WHERE condition" 1
			return
		fi
	fi
	rollback=0
	wa=($(echo "$where" | sed -e "s/, /,/g"))
	get_pk $db $table
	pkc=$(echo $pk | wc -w)
	if [ $skip_checks -eq 0 ]
	then
		pkwa=0
		check_pk_use "$where" $pkc
		if [ $pk_in_use -eq 0 ]
		then
			display "NOTICE: WHERE condition not using PK, switching to PK for safe rollback" 0
			pkwa=1
		fi
	fi
	[ $skip_checks -eq 0 ] && where_in=$(array_idx "$where" "in")
	if [ $where_in -ge 0 ]
	then
		if [ $(echo $where | fgrep -c "=") -ne 0 ]
		then
			display "Sorry, BakaSQL does not support WHERE conditions with a mix of \"=\" and IN() at this time" 1
			return
		fi
		if [ $(echo $where | fgrep -ic " and ") -ne 0 ]
		then
			display "Sorry, BakaSQL does not support WHERE conditions with multiple IN()s at this time" 1
			return
		fi
		c=$(($where_in + 1))
		IFS="," in_set=($(echo "${wa[@]:$c}" | tr -d "() " | sed -e "s/^ *//g" -e "s/ *$//g"))
		#
		#	WHERE key IN (....)
		#
		echo "-- Rollback instructions for query $qc" >> $rollback_file
		for arg in ${in_set[@]}
		do
			saveIFS="$IFS"
			IFS=" "
			rollback_args "$cols" > $resultset_tmpf
			rbs=$(cat $resultset_tmpf)
			IFS="$saveIFS"
			naked_arg=$(echo $arg | tr -d "'")
			if [ $pkwa -eq 1 ]
			then
				saveIFS="$IFS"
				if [ $pkc -gt 1 ]
				then
					IFS=" "
					rollback_pkwhere "$pk" > $resultset_tmpf
					rbw=$(cat $resultset_tmpf)
					IFS="$saveIFS"
					mysql_query "SELECT CONCAT('UPDATE $table SET ', $rbs, ' WHERE ', $rbw, ';') FROM  $table WHERE ${wa[0]}='$naked_arg' /* update 1 */" "$db" >> $rollback_file
				else
					IFS="
"
					mysql_query "SELECT $pk FROM $table WHERE ${wa[0]}='$naked_arg' /* update 2 */" "$db" > $resultset_tmpf
					for row in $(cat $resultset_tmpf)
                                	do
                                        	mysql_query "SELECT $rbs FROM $table WHERE $pk = '$row' /* update 3 */" "$db" > $resultset2_tmpf
                                        	res=$(cat $resultset2_tmpf | sed -e "s/'NULL'/NULL/g")
                                        	echo "UPDATE $db.$table SET $res WHERE $pk = '$row';" >> $rollback_file
                                	done
					IFS="$saveIFS"
				fi
			else
				mysql_query "SELECT $rbs FROM $table WHERE ${wa[0]}='$naked_arg' /* update 4 */" "$db" > $resultset_tmpf
				res=$(cat $resultset_tmpf | sed -e "s/'NULL'/NULL/g")
				if [ "$res" != "" ]
				then
					rollback=1
					echo "UPDATE $db.$table SET $res WHERE ${wa[0]}='$naked_arg';" >> $rollback_file
				fi
			fi
		done
	else
		#
		#	WHERE key = ....
		#
		echo "-- Rollback instructions for query $qc" >> $rollback_file
		if [ $pkwa -eq 1 ]
		then
			rollback_args "$cols" > $resultset_tmpf
			rbs=$(cat $resultset_tmpf)
			if [ $pkc -gt 1 ]
			then
				rollback_pkwhere "$pk" > $resultset_tmpf
				rbw=$(cat $resultset_tmpf)
				mysql_query "SELECT CONCAT('UPDATE $table SET ', $rbs, ' WHERE ', $rbw, ';') FROM  $table WHERE $where /* update 5 */" "$db" >> $rollback_file
			else
				saveIFS="$IFS"
				IFS="
"
				mysql_query "SELECT $pk FROM $table WHERE $where /* update 6 */" "$db" > $resultset_tmpf
				for row in $(cat $resultset_tmpf)
				do
					mysql_query "SELECT $rbs FROM $table WHERE $pk = '$row' /* update 7 */" "$db" > $resultset2_tmpf
					res=$(cat $resultset2_tmpf | sed -e "s/'NULL'/NULL/g")
					echo "UPDATE $db.$table SET $res WHERE $pk = '$row';" >> $rollback_file
				done
				IFS="$saveIFS"
			fi
		else
			if [ $pk_in_use -eq 0 ]
			then
				mysql_query "SELECT COUNT(*) FROM $table WHERE $where /* update 8 */" "$db" > $resultset_tmpf
				count=$(cat $resultset_tmpf)
			else
				count=1
			fi 
			if [ $count -gt 1 ]
			then
				# assumes small table, add a check
				rollback=1
				delete_rollback  "$db" "$table" "$where" 1 >> $rollback_file
			else
				if [ $skip_checks -eq 0 ]
				then
					rollback_args "$cols" > $resultset_tmpf
					rbs=$(cat $resultset_tmpf)
				fi
				mysql_query "SELECT $rbs FROM $table WHERE $where /* update 9 */" "$db" > $resultset_tmpf
				res=$(sed -e "s/'NULL'/NULL/g" $resultset_tmpf)
				if [ "$res" != "" ]
				then
					rollback=1
					# check special case where one of cols being updated is also in where clause
					if [ $skip_checks -eq 0 -a $pk_in_use -eq 1 ]
					then
						amr=0
						for uciw in $cols
						do
							if [[ ${where^^} == *" AND ${uciw^^} "* ]]
							then
								aw=$(echo "$where" | awk -F " AND $uciw" '{print $1}')
								[ "$aw" = "$where" ] && aw=$(echo "$where" | awk -F " and $uciw" '{print $1}')
								amr=$($BAKAUTILS check_pk_use "${aw,,}" "${pk,,}"  2>>/tmp/bakautils.log)
								[ $amr -eq 1 ] && break
							fi
						done
					fi
					if [ $amr -eq 0 ]
					then
						echo "UPDATE $db.$table SET $res WHERE $where;" >> $rollback_file
					else
						echo "-- where condition in the following code was modified to remove updated column $uciw" >> $rollback_file
						echo "UPDATE $db.$table SET $res WHERE $aw;" >> $rollback_file
					fi
				else
					echo "-- row(s) not found with specified WHERE clause, no rollback needed" >> $rollback_file
				fi
			fi
		fi
	fi
	total_errors=$((total_errors-1))
	run_statement "$1" $dryrun
	update_old_fgp="$fgp"
}

show_rollback()
{
	display "<font size=2>---- start of rollback instructions ----" 0
	escape_html "$(cat $1)" > $resultset_tmpf
	d_text=$(cat $resultset_tmpf)
	display "$d_text" 0
	display "---- end of rollback instructions ----</font>" 0
	display "" 0
}

pretty_print()
{
	$BAKAUTILS pretty_print "$1" 2>>/tmp/bakautils.log
}

cm_log_q()
{
	[ $dryrun -eq 1 ] && return
	echo "$1" >> $cmlog_tmpf
}

process_query() {
	q_nb=$(echo "$1" | sed -e "s/^ *//")
	IFS=" " q=($q_nb)
	display "----- Processing query #$2 ------" 2
	if [ ${#1} -gt $MAX_QUERY_SIZE ]
	then
		display "Query too large, maximum allowed query size is  $MAX_QUERY_SIZE. Needs splitted." 1
		return
	fi
	if [ $speed_hacks -eq 0 ]
	then
		rn=$(date "+%Y-%m-%d %H:%M:%S.%3N")
		mysql_debug "($ticket)>-- Query #$2 @ $rn"
		dq="${q[@]}"
		dqq=$(pretty_print "$dq")
		display "$dqq" 2
		if [ "${q[0],,}" != "set" ]
		then
			insert_vars "$1"
		else
			qte="$1"
		fi
	else
		qte="$1"
	fi
	case "${q[0],,}" in
		'update') 
			query_update "$qte" "$2"
			cm_log_q "$qte"
			;;
		'delete') 
			query_delete "$qte" "$2"
			update_old_fgp=""
			cm_log_q "$qte"
			;;
		'insert'|'replace') 
			query_insert "$qte" "$2" "${q[0]}"
			update_old_fgp=""
			cm_log_q "$qte"
			;;
		'select'|'show'|'create'|'drop'|'alter'|'truncate'|'grant'|'drop'|'revoke') 
			display "Sorry, ${q[0]} not supported by BakaSQL. This query will not be executed." 1
			;;
		'set') 
			query_set "$qte" "$2"
			;;
		*) display "Syntax error near \"${q[0]}\"" 1
			total_errors=$((total_errors+1))
			;;
	esac
	display "" 0
}

total_query_count()
{
	unescape_execute "$query" > $totcnt_tmpf
	total_queries=$($BAKAUTILS total_query_count $totcnt_tmpf  2>>/tmp/bakautils.log)
}

advanced_options_toggle()
{
	printf "<script type=\"text/javascript\">\n"
	printf "adv_options();\n"
	printf "</script>\n"
}

progress_bar_visibility_toggle()
{
	printf "<script type=\"text/javascript\">\n"
	printf "overlay();\n"
	printf "</script>\n"
}

progress_bar_init()
{
	printf "<div id=\"overlay\">\n"
	printf "\t<div id=\"barcontainer\">\n"
    	printf "\t\t<div id=\"progressbar\">\n"
    	printf "\t\t</div>\n"
    	printf "\t\t<div id=\"percent\">\n"
    	printf "\t\t</div>\n"
    	printf "\t</div>\n"
    	printf "</div>\n"
	progress_bar 0
	progress_bar_visibility_toggle
}

progress_bar()
{
	perc=$(($1 * 100 / total_queries))
	printf "<script type=\"text/javascript\">\n"
	printf "draw(100,%d);\n" $perc
	printf "</script>\n"
}

progress_bar_dismiss()
{
	progress_bar_visibility_toggle
}

notify()
{
	printf "<script>\n"
	printf "Push.create('BakaSQL speaks...', {\n"
	printf "\t\tbody: '%s!',\n" "$1"
	printf "\t\ticon: '/bakaicon.png',\n"
	printf "\t\trequireInteraction: true,\n"
	printf "\t}\n"
	printf ");\n"
	printf "</script>\n"
}

copy_to_clipboard()
{
	display "</div>" 0
	display "<a class=\"c2cc\" href=\"#c2c\" data-clipboard-target=\"#clip_area\">copy to clipboard</a>" 0
	display "<a name=\"c2c\">" 0
}

cm_integration()
{
	$BASE/sbin/servicenow_integration.sh "$ticket" "$user" "$host" "$db" "$start_time" "$end_time" $cmlog_tmpf
}

printf "Content-Type: text/html; charset=utf-8\n\n"
printf "<HTML>\n"
page_style
printf "<BODY>\n"
printf "<script>Push.Permission.request();</script>\n"
printf "<FONT SIZE=3>\n"
case "$REQUEST_METHOD" in
	'GET');;
	'POST');;
	*) 	printf "Unsupported HTTP method $REQUEST_METHOD";
		printf "$closing_tags\n"
		exit 0;;
esac
if [ "$REQUEST_METHOD" = "POST" ]
then
	post=1
	IFS="
"
	for row in $(tr "&" "\n")
	do
		name=$(echo $row | cut -d"=" -f 1)
		value=$(echo $row | cut -d"=" -f 2)
		case "$name" in
			'user') user="$value";;
			'password') password="$value";;
			'host') host="$value";;
			'schema') default_db="$value";;
			'query') query="$value";;
			'ticket') ticket="$value";;
			'dryrun') 
				[ "$value" = "on" ] && dryrun=1
				;;
			'backq') kill_backq=0
				[ "$value" = "on" ] && kill_backq=1
				;;
			'hacks') speed_hacks=0
				[ "$value" = "on" ] && speed_hacks=1
				;;
			'commit') periodic_commit=0
				[ "$value" = "on" ] && periodic_commit=1
				;;
			'commit_intv') commit_interval="$value"
				;;
			'ninja') 
				[ "$value" = "on" ] && ninja=1
				;;
		esac
	done
fi
if [ $post -eq 1 ]
then
	post_checks
	if [ $post_error -eq 0 ]
	then
		myerr=$(mysqladmin -u "$user" -p"$password" -h "$host" ping 2>&1)
		connected=$(echo "$myerr" | fgrep -c alive)
		if [ $connected -ne 1 ]
		then
			display "$(echo "$myerr" | tail -1)" 1
		else
			if [ $kill_backq -eq 1 ]
			then
				display "Backquotes removed. Please execute dry-run again." 2
				post=0
				show_form
				printf "$closing_tags\n"
				exit 0
			fi
			if [ "$query" = "" ]
			then
				display "Connected to $host" 0
				display "$(mysqladmin -u "$user" -p"$password" -h "$host" version | tail -7)" 0
				post=0
			else
				connection_setup 
				IFS=";"
				total_query_count
				if [ "$ticket" != "" ]
				then
					rollback_file="$BASE/rollback/${user}_${host}_${ticket}_$$.sql"
				else
					rollback_file="$BASE/rollback/${user}_${host}_$(date "+%Y%m%d_%T")_$$.sql"
				fi
				echo "SET NAMES utf8;" > $rollback_file
				echo "BEGIN;" >> $rollback_file
				progress_bar_init
				qc=0
				qo=0
				lq=""
				display "<div id=\"clip_area\">" 0
				unescape_execute "$query" >  $query_tmpf
				while read -rd ";" q
				do
					q1=${q//\\\'}
					q2=${q1//[^\']}
					if [ $((${#q2} % 2)) -eq 1 ]
					then
						if [ $qo -eq 0 ]
						then
							qo=1
							lq="$lq$q;"
							continue
						else
							qo=0
							q="$lq$q"
							lq=""
						fi
					else
						if [ $qo -eq 1 ]
						then
							lq="$lq$q;"
							continue
						else
							[ "$(echo -n $q | tr -d ' ')" = "" ] && continue
						fi
					fi
					qc=$(($qc + 1))
					progress_bar $qc
					process_query "$q" $qc
					if [ $dryrun -eq 0 -a $periodic_commit -eq 1 -a $commit_interval -gt 0 ]
					then
						if [ $((qc % commit_interval)) -eq 0 ]
						then
							if [ $total_errors -eq 0 -a $total_warnings -eq 0 ]
							then 
								mysql_query "COMMIT" > /dev/null
								echo "COMMIT;" >> $rollback_file
								committed_something=1
								mysql_query "BEGIN" > /dev/null
								echo "BEGIN;" >> $rollback_file
							fi
						fi
					fi
				done < $query_tmpf
				progress_bar_dismiss
				if [ $qo -eq 1 ]
				then
					display "statement with unterminated string detected! Inspect the code and fix it to continue." 1
					total_errors=$((total_errors+1))
				fi
				[ $total_errors -eq 0 -a $total_warnings -eq 0 ] &&  echo "COMMIT;" >> $rollback_file || echo "ROLLBACK;" >> $rollback_file
			fi
			if [ $dryrun -eq 1 ]
			then
				copy_to_clipboard
				show_rollback $rollback_file
				display "Dry run results:" 2
				display "Errors: $total_errors  Warnings: $total_warnings<BR>" 2
				if [ $total_errors -gt 0 -o $total_warnings -gt 0 ] 
				then
					display "There are errors or warnings. Please resolve the problem(s) and retry the dry run." 2
				else
					display "This was a dry run. Please verify the rollback code above, then remove the flag to execute the query." 2
				fi
				mysql_query "ROLLBACK" > /dev/null
				rm -f $rollback_file ${rollback_file}_*_dump.gz 
				notify "dry run of $ticket completed"
			else
				if [ $qc -gt 0 ]
				then
					if [ $total_errors -gt 0 -o $total_warnings -gt 0 ] 
					then
						mysql_query "ROLLBACK" > /dev/null
						if [ $periodic_commit -eq 0 ]
						then
							rm -f $rollback_file ${rollback_file}_*_dump.gz 
							display "Execution failed!  Your changes have been rolled back.  Errors: $total_errors  Warnings: $total_warnings" 1
						else
							if [ $committed_something -eq 0 ]
							then
								rm -f $rollback_file ${rollback_file}_*_dump.gz 
								display "Execution failed!  Your changes have been rolled back. Nothing has been committed.  Errors: $total_errors  Warnings: $total_warnings" 1
							else
								display "Execution failed, but due to periodic commit being ON some statements have been committed before the first error was encountered.<BR>Check rollback file for statements that were already committed,and rollback them NOW. Errors: $total_errors  Warnings: $total_warnings" 1
							fi
						fi
						notify "$ticket failed!"
					else
						mysql_query "COMMIT" > /dev/null
						end_time=$(mysql_query "SELECT DATE_FORMAT(UTC_TIMESTAMP(), '%d-%m-%Y %H:%i:%S')")
						display "Done. Rollback statements saved in $rollback_file on $(hostname)." 0
						copy_to_clipboard
						cm_integration
						notify "$ticket is done!"
					fi
				fi
			fi
		fi
	fi
else
	dryrun=1
fi
show_form
printf "$closing_tags\n"
exit 0
