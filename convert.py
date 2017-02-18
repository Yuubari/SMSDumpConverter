# XML dump converter
import pprint, datetime, sys
from argparse import ArgumentParser

import parsers.SMSBackupAndRestoreXML as Android
import parsers.WindowsSMSBackupXML as WindowsMobile

def parseCommandLine():
	formats = {'windows': 'windows', 'android': 'android'}
	parser = ArgumentParser(description = "XML SMS Dump Converter", epilog = "Compatible with: contacts+message backup on Windows (https://www.microsoft.com/en-us/store/p/contacts-message-backup/9nblgggz57gm) and SMS Backup and Restore on Android (https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)")
	parser.add_argument('-s', '--source', help = 'Source XML file', dest = 'sourcefile', metavar = 'source_file', required = True)
	parser.add_argument('-o', '--output', help = 'Output XML file', dest = 'destfile', metavar = 'destination_file', required = True)
	parser.add_argument('-f', '--sourceformat', help = 'Source XML format (default: windows)', dest = 'sourceformat', default = formats['windows'], choices = list(formats.keys()))
	args = parser.parse_args()
	return (args.sourcefile, args.sourceformat, args.destfile)

def main():

	(sourcefile, sourceformat, destfile) = parseCommandLine()

	if sourceformat == 'windows':

		doc = WindowsMobile.parse(sourcefile, silence = True)
		length = len(doc.Message)
		messages = Android.smses(backup_date = datetime.datetime.now().timestamp()*1000)

		for counter, message in enumerate(doc.Message, 1):
			print("Converting: %6d/%d" % (counter, length), end='\r')

			# Convert FILETIME/ActiveDirectory/LDAP timestamp to Android's UNIX-based milliseconds timestamp
			timestamp = round(message.LocalTimestamp/10000 - 11644473600*1000)
			# Produce a human-readable date
			readable_date = datetime.datetime.fromtimestamp(round(timestamp/1000)).strftime("%d %b %Y %H:%M:%S")

			# Process incoming messages
			if message.IsIncoming == "true":
				converted = Android.smsType(
					protocol = 0, 
					address = message.Sender, date = timestamp, 
					type_ = 1, 
					subject = "null", body = message.Body, 
					toa="null", sc_toa="null", service_center = "null", 
					read = message.IsRead, 
					status = -1,
					locked = 0, date_sent = 0,
					readable_date = readable_date,
					contact_name = "(Unknown)",
					)
				messages.add_sms(converted)
			# Process outgoing messages
			else:
				for r_count, recipient in enumerate(message.Recepients.string, 1):
					converted = Android.smsType(
						protocol = 0, 
						address = recipient, date = timestamp, 
						type_ = 2, 
						subject = "null", body = message.Body, 
						toa="null", sc_toa="null", service_center = "null", 
						read = message.IsRead, 
						status = 0,
						locked = 0, date_sent = 0,
						readable_date = readable_date,
						contact_name = "(Unknown)",
						)
					messages.add_sms(converted)

		with open(destfile, "w", encoding="utf8") as outfile:
			outfile.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n")
			messages.export(outfile, 0)

		print("\nDone. Total messages processed for output: %d." % len(messages.sms))
		if (len(messages.sms) > length):
			print("Multiple-recipient messages were detected, so there are more messages in the output dump.")

	else:
		doc = Android.parse(sourcefile, silence = True)
		length = len(doc.sms)
		#messages = Android.smses(backup_date = datetime.datetime.now().timestamp()*1000)
		messages = WindowsMobile.ArrayOfMessage(
			xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance", 
			xmlns_xsd="http://www.w3.org/2001/XMLSchema",
			)

		for counter, message in enumerate(doc.sms, 1):
			print("Converting: %6d/%d" % (counter, length), end='\r')

			converted = WindowsMobile.MessageType(
				Body = message.body,
				IsRead = message.read,
				LocalTimestamp = (int(message.date)*10000 + 11644473600*10000000),
				IsIncoming = "false" if message.type_ == "2" else "true",
				)

			if message.type_ == "2":
				converted.Recepients = WindowsMobile.Recepients()
				converted.Recepients.add_string(message.address)
			else:
				converted.Sender = message.address

			messages.add_Message(converted)

		with open(destfile, "w", encoding="utf8") as outfile:
			outfile.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n")
			messages.export(outfile, 0)

	return 0

if __name__ == "__main__":
    main()