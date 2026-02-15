#!/bin/bash -xe
cd /var/www/html
cp ./wp-config-sample.php ./wp-config.php
sed -i "s/'localhost'/'${db_host}'/g" wp-config.php
sed -i "s/'database_name_here'/'${db_name}'/g" wp-config.php
sed -i "s/'username_here'/'${db_user}'/g" wp-config.php
sed -i "s/'password_here'/'${db_password}'/g" wp-config.php