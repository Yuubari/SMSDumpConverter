XML Dump Parser
===============

An extremely simple (and ugly, code-wise) converter written using the extremely helpful [generateDS](https://pythonhosted.org/generateDS/) script by [Dave Kuhlman](http://www.davekuhlman.org/).

Supports [contacts+message backup](https://www.microsoft.com/en-us/store/p/contacts-message-backup/9nblgggz57gm) for Windows phones and [SMS Backup and Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore) for Android. Only converts SMS data. Does not support MMS data, call logs, etc.

Source code requires Python 3.x with lxml. Binary “distribution” does not require anything.