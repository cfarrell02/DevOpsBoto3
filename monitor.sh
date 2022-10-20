#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2
#
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)

#Calculates CPU usage as a percentage
CPUUSAGE=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}') #Taken from https://stackoverflow.com/questions/9229333/how-to-get-overall-cpu-usage-e-g-57-on-linux


#Measures disk usage on drives

DISKUSAGE=$(df -h | grep /dev/)


#Runs a speedtest from the instance
SPEEDTEST=$(speedtest --accept-license -f json-pretty | grep -n bandwidth )
DOWNSPEED=$(echo "$SPEEDTEST" | grep 11)
DOWNSPEED=$(expr substr "$DOWNSPEED" 25 7)
DOWNSPEED=$(( $DOWNSPEED / 125000 ))
UPSPEED=$(echo "$SPEEDTEST" | grep 22)
UPSPEED=$(expr substr "$UPSPEED" 25 7)
UPSPEED=$(( $UPSPEED / 125000 ))

echo -e "\nDisk Usage: \n$DISKUSAGE\n"
echo "CPU Usage: $CPUUSAGE"
echo "Instance ID: $INSTANCE_ID"
echo "Memory utilisation: $MEMORYUSAGE"
echo "No of processes: $PROCESSES"
echo "Speedtest download speed: $DOWNSPEED Mbps"
echo "Speedtest upload speed: $UPSPEED Mbps"


if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi