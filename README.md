# Crowdsourcing Study

This markdown contains configurations and instructions to setup a server for the crowdsourcing study.

There are four core elements of the project:

* DNS server configuration
* Apache module for IPv6 from (https://github.com/falling-sky/source/wiki)
* Python Django server to host a website and collect data
* Amazon scripts to create tasks on Amazon Mechanical Turk (Mturk)

We will cover each one of them and provide our configuration files and source code as an example to reproduce the study.

We are using the following notations in the document and source code (please replace according to your configuration):


* SERVER1IPv4 (IPv4 Address of server 1)
* SERVER1IPv6 (IPv6 Address of server 1)
* SERVER2IPv4 (IPv4 Address of server 2)
* SERVER2IPv6 (IPv6 Address of server 2)
* example.com (Our example domain)
* ns1 (Name server configured on server 1)
* v6ns1.v6ns (Name server configured on server 2)

## Server and software requirements

We need two servers for our configuration, the following software was used in our setup:

- Server1 (Public IPv4 and IPv6 Address):
    + Ubuntu 14.04
    + Bind9
    + Apache/2.4.18 server
    + Python Django
    + Certbot (Let's Encrypt)
    + Python 3
    + Python boto3 (Amazon Mturk)
    + Python SQS (Amazon Mturk)

- Server2 (Public IPv4 and IPv6 Address):
    + Ubuntu 14.04
    + Bind9
    + Apache/2.4.18 server
    + Certbot (Let's Encrypt)

## DNS configuration

In our setup, we need two DNS servers, one of the servers acts as the main server; it replies to A (IPv4) queries while also delegating queries to the other server. The second server is a "v6 only" DNS server and responds to AAAA queries. Detailed documentation can be found [here](https://github.com/falling-sky/source/wiki/InstallDNS)

One of the critical requirements for this setup is to configure an authoritative DNS server for a registered domain. In the majority of the cases, domain registrars configure a nameserver by themselves. After discussing with a number of registrars, we were able to convince 123-reg.co.uk. They kindly allowed us to configure our own nameserver and added to the TLD's zone file the corresponding NS record and its glue record pointing towards our server instead of the server of domain registrar.


### Server1 setup

In our topology, nameserver1.example.com will act as the main server and will reply to IPv4 requests, it will delegate IPv6 queries to v6ns1.v6ns.example.com.

We define several subdomains to capture network configurations of machines. You can read more details about these tests here.

!TODO: Missing link for 'here' with more infos on tests!

Our zone file for server1 is as follows (please replace the domains and IP addresses according to your configuration):

```
;################################################################
;# ZONE: example.com.
;# Put this on your real name servers.  Fix the SOA and NS
;# to reflect your environment.
;################################################################
$ORIGIN example.com.
$TTL 0
@       IN SOA example.com. hostmaster.example.com. (
  201801209 ; Serial
  86400 ; Refresh
  7200  ; Retry
  604800 ; Expire
  0) ; Minimum

; main domain name servers
@               IN  NS  ns1
ns1             IN  A   SERVER1IPv4  ; glue
v6ns1.v6ns      IN      AAAA    SERVER2IPv6 ; glue

; Main web site is intentionally IPv4 only, per the FAQ.
$TTL 0 ;
@               A       SERVER1IPv4

; Specific records for tests
ipv4            A       SERVER1IPv4
ipv6            AAAA    SERVER1IPv6
mtu1280         AAAA    SERVER1IPv6
ds              A       SERVER1IPv4
ds              AAAA    SERVER1IPv6
www             A       SERVER1IPv4
cs              A       SERVER1IPv4
cs              AAAA    SERVER1IPv6

; sub-domain definitions
; zone fragment for us.example.com
$ORIGIN v6ns.example.com.
$TTL 0 ;
@               IN  NS  v6ns1.v6ns.example.com.
```

### Server2 setup

As discussed earlier server2 will only respond to IPv6 queries. An example for zone file for server2 is as follows:

```
;################################################################
;# ZONE: v6ns1.example.com.
;# Put this on the VM operating your test-ipv6.com mirror.
;# Do NOT put this on your main DNS server.
;################################################################

$TTL 0
@       IN SOA v6ns.example.com. hostmaster.example.com. (
  20180117 ; Serial
  86400 ; Refresh
  7200  ; Retry
  604800 ; Expire
  0) ; Minimum

@               IN  NS  v6ns1
v6ns1             IN AAAA   SERVER2IPv6  ; glue

$TTL 0
@                AAAA    SERVER2IPv6

; Specific records for tests
ipv4            A       SERVER2IPv4
ipv6            AAAA    SERVER2IPv6
ds              A       SERVER2IPv4
ds              AAAA    SERVER2IPv6
a               A       SERVER2IPv4
aaaa            AAAA    SERVER2IPv6
www4            A       SERVER2IPv4
www6            AAAA    SERVER2IPv6
v4              A       SERVER2IPv4
v6              AAAA    SERVER2IPv6
```

### Validation

To validate your configuration, please run the following commands.

**1. Test for DNS configuration:**

```
dig +short @4.2.2.1 example.com
```

This will query Verizon's open public DNS resolver for the configured site. It should return the IPv4 address. You can also test other subdomains that we have configured earlier.


**2. Test for IPv6 DNS configuration with IPv4 DNS server:**

```
dig @4.2.2.1 ds.v6ns.example.com a
```

Verizon's IPv4-only DNS servers are unable to look up the IPv6-only servers. **This test must fail.**


**3. Test for IPv6 DNS configuration with IPv6 DNS server:**

```
dig @8.8.8.8 ds.v6ns.example.com a
```

Now try using Google's DNS server. **This test must succeed** as Google's DNS servers can lookup IPv6 addresses.


## Installing falling-sky module to run tests

**Make sure you do these configurations with correct paths on both servers.** Download and install the falling-sky module on Server1 and Server2. You can read more about the installation and components [here](https://github.com/falling-sky/source/wiki/Install).

```
rsync -av fsky@rsync.test-ipv6.com:stable/mod_ip .
cd ./mod_ip
./configure
make
make install
```

In the final step, we will download the content and place it in a folder accessible by the web. In our case, we created the following directory `/var/www/example.com/public_html/`. We will configure this directory to be used by Apache later in this tutorial.

To download the content use the following command:

```
rsync -av fsky@rsync.test-ipv6.com:stable/content/. /var/www/example.com/public_html/.  --delete --exclude site
```

We will need to edit `/var/www/example.com/public_html_/site/config.js`. The configuration is required on both servers. For server2 we created a subdomain v6ns.example.com. Change the value of the domain and IP addresses based on the server you are configuring this.

```
MirrorConfig =
{

    "site": {
          "name": "test-ipv6.example.com",
              "contact": "YOUR NAME",
                  "mailto": "YOUR EMAIL"
                      },

      "load": {
            "domain": "example.com",
              "ipv4": "SERVERIPv4",
              "ipv6": "SERVERIPv6"
               },

        "footer": {
              "#logo": "/site/logo.png",
                  "#operator": "Jason Fesler",
                      "#link": "http://test-ipv6.com",
                          "#html": "/site/footer.html"
                              },

          "options": {
                "show_stats": "/stats.html",
                "survey": "/survey.php",
                "comment": "/comment.php",
                "ip": "/ip/"
          },

            "facebook": {
                  "enable": 0
                      },
              "twitter": {
                    "enable": 0,
                        "name": "testipv6com"
                            }
}
```

## Get SSL certificates

We used Let's Encrypt TLS certificate service for our website, as crowdsourcing platforms require encrypted traffic. They are free and very easy to configure. Please follow the [tutorial](https://letsencrypt.org/getting-started/) to get certificates for the domains and subdomains we have configured earlier in our zone files.


## Configuring Apache Server

The next step is to load mod_ip module provided by falling-sky in Apache. Edit `/etc/apache2/mods-available/mod_ip.load` and add the following line with the correct path:

```
LoadModule mod_ip_module /usr/lib/apache2/modules/mod_ip.so
```

Run the following command to enable the module:

```
a2enmod mod_ip
```


We used the following configuration in our default Apache config file `/etc/apache2/sites-available/`:

```
<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname, and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName www.example.com
        ServerAlias ds.v6ns.example.com
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/v6ns.example.com/public_html


        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        <Directory "/var/www/v6ns.example.com/public_html">
                Options MULTIVIEWS Indexes FollowSymLinks
                 AllowOverride ALL

                #
                # Controls who can get stuff from this server.
                #
                Order allow,deny
                Allow from all

        </Directory>


</VirtualHost>
Listen 443

<VirtualHost *:443>
 ServerName ipv6.example.com
 SSLEngine on


 SSLCertificateFile    /etc/letsencrypt/live/ipv6.example.com/cert.pem
 SSLCertificateKeyFile  /etc/letsencrypt/live/ipv6.example.com/privkey.pem
 SSLCertificateChainFile   /etc/letsencrypt/live/ipv6.example.com/chain.pem


        <Directory "/var/www/v6ns.example.com/public_html">
                Options MULTIVIEWS Indexes FollowSymLinks
                #
                # AllowOverride controls what directives may be placed in .htaccess files.
                # It can be "All", "None", or any combination of the keywords:
                #   Options FileInfo AuthConfig Limit
                #
                 AllowOverride ALL

                #
                # Controls who can get stuff from this server.
                #
                Order allow,deny
                Allow from all

        </Directory>


</VirtualHost>
```

Now, you should be able to test your setting by going to www.example.com. If everything is working, you should get a page similar to [the original Test IPv6 website](https://test-ipv6.com/).


## Python Django Application

We used a Python Django web server for our website. The Following edits are required in the code and file settings to make the application work. The scripts used by us can be found in the settings folder.

In the `settings.py` file change the following lines and add your domain and IPv4 address according to your configuration. Also, add your application key.

```
SECRET_KEY = ''
ALLOWED_HOSTS = ['SERVER1IPv4','www.example.com','example.com', 'cs.example.com']
```

* models.py contain the database schema. We have IPv6 and IPv4 test properties in IPAddresses table, while we save results from Amazon and Prolific tables in ProA and AmazonResults table. This file is located in testipv6 folder.

* To change the HTML text you can edit `templates/index.html`. The current page dynamically offers content for Prolific or Amazon based on URL parameters.

* views.py holds the main logic of the program. It detects which platform (Prolific or Mturk) a user is coming from and sends parameters to load the correct web page. You need to add your AWS access and secret key in the functions add_qual and get_qualTypeID. These functions ensure each worker from Amazon can only participate once.


## Amazon Mturk automation scripts

Finally, we provide scripts to create tasks, pay users and download submissions. You need to install and configure Python boto3 package. For more details please visit [the API documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html).

The Python scripts which are provided are explained below:

* create_qualification.py is used to create an auto-assigned qualification given to users once they submit a completed task. This program is used to limit one submission per user. You need to run this script before creating hits.

* create_hits.py can be used to create tasks; you can change the reward per assignment, text for your task, and the total number of jobs you want to create from this program. The create_hits function creates the number of required submission.

* Amazon Simple Queue Service (SQS) needs to be configured for notifications of submissions. Read more about SQS and configuring policy for Mturk [here](https://aws.amazon.com/sqs/). After configuring SQS, you can use create_queue.py which will queue the submissions and send notifications.

* Add your policy to create_notification.py, this will notify you as soon as there is a submission.

* You can use the pay_users.py script to pay users who have submitted the task. Please note that it will pay all users.

* If you want to delete the hits, you can use delete_hits.py script to delete all the created tasks.

* If you want to restart the campaign, and want to allow users who have previously participated you, can use delete_qual_workers.py to remove the restriction.

* process_message.py script needs to be run as a background process; it will wait for a new submission and then call the updateDB.py script to update the database with the results of submission.
