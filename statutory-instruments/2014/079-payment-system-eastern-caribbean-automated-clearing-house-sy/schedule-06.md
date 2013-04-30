SCHEDULE 1
(rules (5(1), (2), 33, 86, 87,
102, 104, 108, 113, 118, 121, 131,132,
135, 138, 145, 147, 161, 166,
168, 169, 172, 173)
FILE SPECIFICATIONS
File Specifications
    (1) The ECACH System shall comply with the full ANSI X9.100-
187 Standards for cheque image exchange and the NACHA Standard
for electronic payment files. However, modifications have been made
to accommodate the needs of the Currency Union.
NACHA Standard
    (2) The Full NACHA Standard for the electronic payment files shall
be accepted and processed by the ECACH system with the following
modifications -

(a)  In order to allow for domestic multicurrency clearing and
settlement, the Reference Field in the File Header Record
will be a mandatory field used to indicate currency code.  The
“three character” ISO Currency Code for EC dollar and US
dollar will be used.

(b)  The Central Bank is not using a check digit with the bank
routing number scheme.  A trailing zero will be used in any
9 digit Routing Number field, a zero will be used in any
Bank Routing Number Check Digit field and there will be no
validation on the check digit.

(c)  An additional operator code is being added “R62–originating
participant exceeds collateral” to identify an operator return
at the end of day if the originating participant does not have
enough collateral to send the payments.

NACHA Standard entry class codes
    (3) The following NACHA Standard entry class codes shall be used
for processing -

(a)  CIE – Customer Initiated Entry: Customer initiated entries
are limited to credit applications where the customer initiates
the transfer of funds to a person for payment of funds owed
to that company or person. Typical examples of these entries
are utility bills and other internet banking product payments.

(b)  PPD – Prearranged Payment or Deposit Entry.

(i)  Direct Deposit: Direct deposit is a credit application that
transfers funds into a customer’s account at the receiving
participant.  The funds being deposited can represent a
variety of products such as payroll, remittances, interest,
pension and dividends refunds.

(ii) Preauthorised Payment: A preauthorised payment is a
debit application.  Companies with existing relationships
with the customers may participate in the electronic funds
transfers through the electronic transfer (Direct Debit)
of payment entries.  Through standing authorisations,
the customer grants the company authority to initiate
periodic charges to his or her account as bills become
due.  This concept is especially applicable in situations
where the recurring bills are regular and do not vary in
amount such as insurance premiums and loan instalments.
Preauthorised payments may also be used for bills where
the amount does vary, such as utility payments.

(c)  CCD/CCD+ – Corporate Credit or Debit: This application
can be either a credit or a debit application where funds are
either distributed or consolidated between corporate entities
or government entities.  This application can serve as a stand-
alone funds transfer between corporate or government entities,

or it can support a limited disclosure of information when the
funds are being transferred between organizations (that is sister
companies) under the same group.

(d)  CTX – Corporate Trade Exchange: This application supports
the transfer of funds (debit or credit) with a trading partner
relationship in which business payment remittance information
is sent with the funds transfer.  The payment-related
information is placed in multiple addenda records in a format
agreed to by the parties and the ECACH.

(e)  IAT – International ACH: This application supports the
cross-border transfer of funds (debit or credit) by a customer
or business to pay another customer or business in another
territorial jurisdiction.

(f)  ADV – Automated Accounting Advice.

(g)  COR – Automated Notifications of Change or Refused
Automated Notification of Change.

(h)  Returns – Returns, Dishonoured Returns, Contested
Dishonoured Returns.

(i)  Pre-notifications – 0.01 dollar test file for credit or debit
transactions.

(j)  File Acknowledgments – ECACH acknowledgment of file
status.
ANSI X9.100-187 Standards
    (4) The full ANSI X9.100-187 Standards for cheque images will
provide a structure to facilitate electronic exchange of cheque related data
and images for the purpose of forward cheque presentment, return item
notification, and returns processing with the following modifications -

(a)  In order to allow for domestic multicurrency clearing and
settlement, Field 13 in the File Header Record will be a
mandatory field used to indicate currency code.

(b)  The three character ISO Currency Code for EC dollars and
US dollars will be used.

(c)  The Central Bank is not using a check digit with the bank
routing number scheme.  A trailing zero will be used in any 9
Digit Routing Number field, a zero will be used in any Payer
Bank Routing Number Check Digit field and no modulus
verification checks will be employed.

(d)  “Return Code P” will be used to identify an operator return
at the end of day if the receiving participant does not have
enough collateral to cover the payment.
Failure to meet standards
    (5) Where a system participant fails to meet the standards as
prescribed by these Rules the batch or file which does not meet the
standards may be rejected by the operator.  A receiving participant may
return individual entries which do not meet the standards.
