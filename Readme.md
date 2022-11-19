# Simple tools:

<h2> Detect&PortScanner: a port scanner and detector</h2>

PSDetect will use the pcapy library to listen to incoming connections,
and report the presence of a scanner if a single machine attempted to connect to 15 or more consecutive
ports within a 5 second window. PSDetect should therefore be able to detect when PortScan is used.
PSDetect should listen on all network interfaces, and should take no arguments. It should not produce
any output until a scanner is detected. When a scanner is detected, it should print out the message:
Scanner detected. The scanner originated from host A.B.C.D.
Where A.B.C.D should be replaced with either the IP address or the hostname of the machine that attempted
to connect to 15 or more consecutive ports within a 5 second window. PSDetect will use impacket library
to get the IP header out of Ethernet frames returned via pcapy listening function

<h2> BulkDelay: bulk-delay Subtitle of a srt file</h2>
<strong>usage:  bulkDelay(OldSrt, NewSrt, Opp, time)
</br><strong>OldSrt</strong>: the old Srt file Path
</br><strong>NewSrt</strong>: the new Srt file Path
</br><strong>Opp</strong>: "Add" or "Sub"
</br><strong>time</strong>: the time to add/subtract

<h2> diffie-hellman</h2>
Share a symmetric key between a client and server using Diffie‐Hellman protocol.

</br>
<h2> FreqAnalysis</h2>
finding the number of Frequency every letter is in a text file.

</br>
<h2> GPA_calculator</h2>

important setup:
<b>important setup: </b>
<br>
in the inputfilepath, the file should have the courses grades in the following format:
<br>
course	weight	letter
<br>
-this is an example of the input file:
<br>
MATH101 4 C+
<br>
MATH102 4 -
<br>
MATH102 3 D
<br>
<br>
how to use the code:
<br>
course_records = Get_records_from_file(inputfilepath="courses_records.txt", GPA_weight=4)
<br>
print(Put_data_in_file(course_records=course_records, outputfile="Final_GPA.txt"))

<h2> PicSteg</h2>

Check "PicSteg.py -h"
"Make sure to check all images before using, this script doesn't check for correctness"
usage:

1: PicSteg.py Hide [-h] --images IMAGES [IMAGES ...] --secret SECRET --NewImage NEWIMAGE

2: PicSteg.py Unhide [-h] --SecretImages SECRETIMAGES [SECRETIMAGES ...] --NewFile NEWFILE

<h2> SymmetricKey-AES</h2>
Encrypt/Decrypt text file using symmetric key algorithm (AES)
</br>
<h2> PublicKey-RSA</h2>
Generate an asymmetric key pair (public and private) 
Decrypt/Encrypt the text file using the private key

</br>
<h2>isPrime</h2>
finding prime numbers can take a long time, this show case optimization scenario

</br>
<h2>K-Anonymization</h2>
implementing K-Anonymization algorithm#� �S�i�m�p�l�e�T�o�o�l�s�-�
�
�
