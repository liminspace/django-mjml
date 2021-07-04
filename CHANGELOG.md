0.11.0 (2021-07-04)
===================
 * Added supporting Django v3.2
 * Added Python 3.9 in tests
 * Added MJML 4.10.1 in tests
 * Removed Python 3.5 from tests
 * Removed MJML older than 4.4.0 from tests
 * Upgraded Node to v14 for tcp-server
 * Upgraded MJML to 4.9.3 in dockerfile
 * Moved from Travis to GitHub Actions


0.10.2 (2020-08-28)
===================
 * Import `requests` only if it's really needed


0.10.1 (2020-08-16)
===================
  *  Added supporting Django v3.1


0.10.0 (2020-06-29)
===================
  * Added `requests` in extras require in `setup.py`
  * Added MJML 4.6.3 in tests
  * Upgraded MJML to 4.6.3 in dockerfile
  * Updated docs


0.9.0 (2019-12-24)
==================
  * Added supporting Django v3.0
  * Added supporting render http-server (including official MJML API https://mjml.io/api)
  * Added Python 3.8 in tests
  * Added MJML 4.5.1 in tests
  * Upgraded MJML to 4.5.1 in dockerfile
  * Upgraded Node to v12 for tcp-server
  * Reorganized tests
  * Updated docs


0.8.0 (2019-07-29)
==================
  * Fixed a trouble with unicode
  * Added MJML 4.4.0 in tests
  * Upgraded MJML to 4.4.0 in dockerfile


0.7.0 (2019-04-06)
==================
  * Removed MJML 4.0.5, 4.1.2 and 4.2.1 from tests
  * Added MJML 4.3.1 in tests
  * Updated tcp-server adding cleanly termination
  * Upgraded MJML to 4.3.1 in dockerfile
  * Updated dockerfile by using `exec`
  * Added supporting Django v2.2


0.6.0 (2018-12-06)
==================
  * Added `MJML_CHECK_CMD_ON_STARTUP` setting (thanks to Marcel Chastain)
  * Added Python 3.7 in tests
  * Added MJML v.4.2.1 in tests
  * Removed MJML v.2.3.3 from tests
  * Updated MJML to 4.2.1 in dockerfile


0.5.4 (2018-10-19)
==================
  * Fixed Popen PIPE subprocess deadlock by using TemporaryFile for stdout


0.5.3 (2018-08-07)
==================
  * Added supporting MJML v4.1.2
  * Added supporting Django v2.1
  

0.5.2 (2018-06-29)
==================
  * Added supporting MJML v4.1.0
  * Added .pyup.yaml
  * Updated tests
  * Added dockerfile for tcpserver
  * Remove mjml 3.0.2, 3.1.1 and 3.2.2 from tests


0.5.1 (2018-06-05)
==================
  * Add stopping tcpserver on SIGINT


0.5.0 (2018-04-28)
==================
  * Add support MJML v4
  * Tcpserver doesn't skip mjml errors now (thanks @yourcelf)
  * Refactor arguments in tcpserver
  * Fix incomplete sending data via socket (thanks @cavanierc)


0.4.0 (2018-01-10)
==================
  * Add support Django 2.0
  * Update support new versions of MJML (up to 3.3.5)


0.3.2 (2017-04-06)
==================
  * Add support Django 1.11


0.3.1 (2017-03-18)
==================
  * Update support new versions of MJML (up to 3.3.0)


0.3.0 (2017-03-03)
==================
  * Update support new versions of MJML (up to 3.2.2)
  * Add support Python 3.6


0.2.3 (2016-10-13)
==================
  * Add supporting django 1.8
  

0.2.2 (2016-08-15)
==================
  * Check mjml only if mode is "cmd"


0.2.1 (2016-08-03)
==================
  * Add support Django 1.10
  

0.2.0 (2016-07-24)
==================
  * Add backend mode TPCServer
  * Remove Python 3.4 from tests
  * Upgrade Django to 1.9.8 in tests
  

0.1.2 (2016-05-01)
==================
  * Fix release tools and setup.py


0.1.0 (2016-04-30)
==================
  * Migrate to MJML 2.x
  * Add support Python 3.4+


0.0.1 (2016-04-19)
==================
  * First release
