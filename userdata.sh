#!/bin/bash
yum update -y
yum install httpd -y
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.rpm.sh | sudo bash
yum install -y speedtest

systemctl enable httpd
systemctl start httpd
echo "<!doctype html>
<html>
  <head>
    <style>
      *{font-family: Arial, Helvetica, sans-serif}
    </style>
    <title>EC2 Instance Page</title>
  </head>
  <body>
	<h1>EC2 Instance Details</h1>
    <p>This page has the metadata for this EC2 instance</p>
<br>
<p>CA Project - Cian Farrell - 20094046</p>
<p>
" > /var/www/html/index.html
echo "Instance ID is: " >> /var/www/html/index.html
curl -s http://169.254.169.254/latest/meta-data/instance-id >> /var/www/html/index.html
echo "<br>\nAMI ID is: " >> /var/www/html/index.html
curl -s http://169.254.169.254/latest/meta-data/ami-id >> /var/www/html/index.html
echo "<br>\nInstance Type is: " >> /var/www/html/index.html
curl -s http://169.254.169.254/latest/meta-data/instance-type >> /var/www/html/index.html
echo " </p></body></html>" >> /var/www/html/index.html