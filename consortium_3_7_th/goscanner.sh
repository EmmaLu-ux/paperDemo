#!/bin/bash

#export PATH=/home/tls13/tls13/go/bin/:$PATH

export LC_ALL=C

INFILE=$1
INFILE_BASE=`basename $1`
OUTPUT_DIR=$2
#META_DIR=${OUTPUT_DIR}/meta
#USER=$3

LOG=$3

GOSCANNER_LOG_FILE=${LOG}/${INFILE_BASE}.goscanner.log
GOSCANNER_OUTPUT_DIR=${OUTPUT_DIR}/
#TCPDUMP_OUTPUT_FILE=${OUTPUT_DIR}/${INFILE_BASE}.goscanner.tcpdump.pcap
#TCPDUMP_LOGFILE=${META_DIR}/${INFILE_BASE}.goscanner.tcpdump.log

#mkdir -p $META_DIR

# Increase file limit
ulimit -Hn 1024000
ulimit -Sn 65535

# TCP: too many orphaned sockets
#echo 16384 > /proc/sys/net/ipv4/tcp_max_orphans

# Adjust as needed
GOSCANNER=/home/z/webemail-https/http-header/tools/goscanner/goscanner
GOSCANNER_CONF_FILE=/home/z/webemail-https/http-header/tools/goscanner/goscanner.conf
#TCPDUMP=/usr/sbin/tcpdump
#TCPDUMP_IFACE=eth0

# Create meta file
#echo $DATE >> ${META_DIR}/$INFILE_BASE.goscanner.meta

#time=$(date "+%Y%m%d-%H%M%S")
#echo $time >> ${META_DIR}/$INFILE_BASE.goscanner.meta

# copy configuration
#CONF_BASENAME=`basename $GOSCANNER_CONF_FILE`
#cp $GOSCANNER_CONF_FILE $META_DIR/$INFILE_BASE.$CONF_BASENAME

# shuffle input
#shuf $INFILE > $INFILE.shuf

# run tcpdump
#$TCPDUMP -n -i $TCPDUMP_IFACE -w $TCPDUMP_OUTPUT_FILE "tcp port 443" 2> $TCPDUMP_LOGFILE &
#TCPDUMPPID=$!
#sleep 5

# run goscanner
$GOSCANNER -C $GOSCANNER_CONF_FILE -i $INFILE -o $GOSCANNER_OUTPUT_DIR -q 80 -l $GOSCANNER_LOG_FILE


# stop tcpdump
#/bin/kill -INT $TCPDUMPPID
#sleep 5

# rename output files
#mv $OUTPUT_DIR/hosts.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.hosts.csv
#mv $OUTPUT_DIR/http.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.http.csv
#mv $OUTPUT_DIR/certs.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.certs.csv
#mv $OUTPUT_DIR/cert_host_rel.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.cert_host_rel.csv

#chown -R $USER:$USER $OUTPUT_DIR
