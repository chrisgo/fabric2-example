# SSL certificates

## We use Letsencrypt "wildcard" certs

With fabric, it is only a couple of steps we have to do every 60-90 days

* `fab dev www renew_cert` <= renews certs on dev-www1 server and copies to local filesystem
* Do a commit (so the new certs get checked in)
* `fab production www renew_cert` <= copies certs to PROD servers and restarts nginx
  * Also do for staging `fab staging www renew_cert`
* We use https://httpscop.com/ to monitor the certs (as of 8/12/20)

## Manual Process

* As of 4/4/2019, we are using dev-www1.domain.com
  * Debian 10 (Buster)
* Wildcard certs use TXT for DNS validation and is done with Amazon R53
* Renewal method
  * ssh username@dev-www1.domain.com
  * `certbot renew` (create DNS entry for TXT)
  * Check in the privkey.pem and fullchain.pem to source control
    * bin/fabfile/environments/ssl/privkey.pem
    * bin/fabfile/environments/ssl/fullchain.pem

---

## Certbot Install

* https://varunpriolkar.com/2018/05/free-wildcard-certs-with-lets-encrypt-dns-auth-ft-route-53/
* `sudo apt install software-properties-common python3-pip`
* `sudo apt install certbot`
* `sudo certbot --version` (should show something like certbot 0.30.2)
* `sudo pip3 install certbot-dns-route53`
* Create file `/root/.aws/config` with the following contents
  * [default]
  * aws_access_key_id=
  * aws_secret_access_key=
* `sudo certbot certonly -d domain.com -d *.domain.com  --dns-route53 --server https://acme-v02.api.letsencrypt.org/directory`

## Check SSL Cert Expire Date

* `openssl x509 -dates -noout < /path/to/fullchain.pem` (or /path/to/certificate)
* https://community.letsencrypt.org/t/how-to-find-certifications-expiry-date/48661

---

# Old Instructions (DO NOT USE)

## Self-signed Cert

* Use openssl to generate CSR
* We are using nginx web server
* Use the private key domain.com.key

`openssl req -new -key domain.com.key -nodes -out wildcard.example.csr`

## Wildcard => use for all other domains and non-www servers

* We use a wildcard for all other domains
* Also use for example MySQL, Redis
* We use AlphaSSL purchased from SSL2Buy.com for $38/year (x 3 years)
* Generate CSR
  * FQDN: *.domain.com
  *

## Comodo ($9/year) Positive SSL => *** OLD ***

* Purchase from Namecheap.com
  * Order
  * Manage SSL Certificate > Activate
* Generate CSR
  * New Key
    * openssl req -nodes -newkey rsa:2048 -keyout {{domain.com}}.key -out {{server.domain.com}}.csr
  * Existing key
    * openssl req -new -key {{domain.com}}.key -out {{server.domain.com}}.csr
  * Field Information
    * Country Name (2 letter code) [AU]: {{US}}
    * State or Province Name (full name) [Some-State]: California
    * Locality Name (eg, city) []: {{City}}
    * Organization Name (eg, company) [Internet Widgits Pty Ltd]: {{Company Name}}
    * Organizational Unit Name (eg, section) []: {{blank}}
    * Common Name (eg, YOUR name) []: {{server.domain.com}}
    * Email Address []: tech@{{domain.com}}
* Wait for email from Comodo
  * Confirm using link & code from email
* Wait for second email from Comodo with zip file
  * Unzip file
  * cd to unzip folder
  * cat {{server}}_{{domain_com}}.crt COMODORSADomainValidationSecureServerCA.crt COMODORSAAddTrustCA.crt AddTrustExternalCARoot.crt >> {{server.domain.com}}.bundle.crt
* Copy key and crt file to server
  * Update nginx to use SSL

* Documentation
  * https://support.comodo.com/index.php?_m=knowledgebase&_a=viewarticle&kbarticleid=3&nav=0,33
  * http://bhira.net/ssl-on-nginx/

## Certbot 9/5/2018

* As of 9/5/2018, we are using dev-php7.domain.com
  * Debian 9 (Stretch)
  * https://www.devcapsule.com/docs/read/letsencrypt-wildcard-nginx-debian-stretch/
* Wildcard certs use TXT for DNS validation and is done with Amazon R53
* Renewal method
  * ssh username@dev-php7.domain.com
  * `certbot-auto renew` (create DNS entry for TXT)
  * Check in the privkey.pem and fullchain.pem to source control
    * bin/fabfile/environments/ssl/letsencrypt/*
    * bin/fabfile-debian9/environments/ssl/letsencrypt/*
