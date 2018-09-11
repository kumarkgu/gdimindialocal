use strict;
use warnings FATAL => 'all';
use Encode qw(encode_utf8);

my ($string, $regex);

sub cleanstring {
    my ($__string) = @_;
    $__string =~ s/\n/ /g;
    $__string =~ s/\s+/ /g;
    $__string =~ s/^\s+//g;
    return $__string;
}

sub industrialestate {
    my $__regex = qr/(?i)[^,]+,\s*([^,]+Industrial Estate),/;
    my $__string = qq{
        Name of the Corporation: Mumbai Manipaytar Description: Ground No .: Gale
        No. 13 and Gale No. 15, Mala No: Ground Floor, Chandragupta Industrial
        Estate, Block No: Andhraari W, Mumbai, Road No: New Link Road (( Survey
        Number: 41; CTS Number: 654;))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub migbuilding {
    my $__regex = qr/(?i)(building no[^,]+\d+[\s\,]*[^,]+MIG)/;
    my $__string = qq{
        1) Name of the Corporation: Mumbai M.P. Other Details:, Other
        Information: Old House No- 321, Floor - ,, Ground, Building No-D-35,
        Model MIG to Oph Hoh Ltd Gandhinagar, M IG Colony, Bandra East Mumbai.
        Instead of the new apartment no .403, floor 4th Wing-A, Rustamji Oriya,
        Model MIG to Oph Soh, Gandhinagar, MIG Colony, Bandra East Mumbai-400051
        - (area of the area 937 sq feet carpet 87 08 CWM carpet) ((CTS Number:
        646pt;))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub corporatepark {
    my $__regex = qr/(?i)[,]\s*([^,]*Park)[,]/;
    my $__string = qq{
        1) Name of the Corporation: Mumbai Manipurer Description: Other
        information: Office No. 1131 (Building No. 11,3 Floor, Unit No 1) Solitare
        Corporate Park, Andheri Ghatkopar Link Road, Andheri East, Mumbai 400093
        .... along with 2 Carparking Space No. 81 and 439 ((CTS Number: 131 and
        others;))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub buildingname {
    my $__regex = qr/(?i)Building Name[\s:\-]*([^,]+)/;
    my $__string = qq{
        Corporation: ..., Other details: Apartment/Flat No:1506, Floor No:15th
        Floor, Building Name:Oberoi Splendor, Block Sector:Jgeshwari East,
        Mumbai - 400060, Road:JVLR, Jogeshwari, City:Andheri, District:Mumbai
        Sub-urban District, HOUSE NUMBER : 1506, Leave and License Months:24
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub nameofbuilding {
    my $__regex = qr/(?i)Name of\s*[the]*\s*Building[\s:\-]*([^,]+)/;
    my $__string = qq{
        1) Name of the corporation: Mumbai Manipatayar Description: Sadanika
        No.: Sadanika No. 1502, Malala No. 15th Floor, Wing Ji, The name of
        building: Mahalaxmi Tower, Block No: Andheri West Mumbai 400053, Road
        No: New DN Nagar , Other Information: Opp Hau Societies Union Ltd. to
        New DN Nagar Along with an ATM (CTS Number: 195 (PART);))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub plotnumber {
    my $__regex = qr/(?i)[,]\s*(Plot N.*Society)\s*,/;
    my $__string = qq{
        1) Name of the Corporation: Mumbai M.P. Details Other: 90% share (part)
        BDR1 / 5122/2016 dated 09/05/2016. 10 percent of the remaining shares
        are paid to the father, the description of the property: - Sr.No. 7, to
        Jain Rajwadi Yes HOW Society Ltd, Plot No. 57, Tarun Bharat Society,
        Opp Cigarette Factory, Chakala Andheri East, Mumbai 400099.530 Sq.-Ft.
        Carpet (CTS Number: 146 151;))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub beforecoop {
    my $__regex = qr/(?i)(\d+[^,]*),[^,]*Society/;
    my $__string = qq{
        1) Name of the Corporation: Mumbai Manipurer Description: Other
        information: Office Unit Number 9159 Floor, Sea Wing, 215 Atrium,
        215 Atrium, Op Premises Society Ltd., Chakala, Andheri Kurla Road,
        Andheri East, Mumbai - 400093 Car parking space number 79B in the
        building's basement. The area of the office unit is 1876 sq ft.
        Carpet, which is 209.21 sq. Meters. CTS No. 25-B Function Chakla and
        CTS No. 215-A Mauge Mulgaon Stamp duty is Rs. 26,41,300 and
        registration fee of Rs. 30,000 / - ((CTS Number: 25-B;)) 2) Name of
        the Corporation: Mumbai Manipatra Description: ((CTS Number: 215-A;))
    };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub buildingnameend {
    my $__regex = qr/(?i)[^,]*,\s*([^,]*(Building|Height|Plaza)(?!')[s]*),/;
    my $__string = qq{
        1) Name of the Municipal Corporation: Mumbai Manipurer Description:,
        Other Information: Office premises area 8000 sq. Foot Built, 12th Floor,
        Hectus House Building, Venkatesh Premises Co.op.source, Plot No. 193,
        Nariman Point, Block-3, Backbe Reclamation Mumbai - 400021 ..... along
        with 3 covered car parking space 59,60,61 executed Deed of Transfer in
        respect of the income. Due date of 07/09/2000 The total stamp duty paid
        on the document is Rs. 1,33,24,200 / - Transfer from transfer deed is
        12,53,00,000 / - Assessing no. ADJ / M / 173/2017 (CTS Number: 1949;))
   };
    $__string = cleanstring($__string);
    print "$__string\n";
    return ($__string, $__regex);
}

sub testlookahead {
    my $__regex = qr/(?i)(Name (and|or) Address Of The\s*)(Debtor|Respondent)*[\s\(]*(Mortgagee)*\)*/;
    my $__string = "Name of the village";
    # my $__string = "Name And address of the debtor";
    # my $__string = "Name And Address Of The Debtor (mortgagee)";
    # my $__string = "Name Or Address Of The Respondent, If The Decree Or Order Of The Court";
    return ($__string, $__regex);
}

#sub buildingnameend {
#    my $__regex = qr/(?i)[^,]*,\s*([^,]*Building)(?!')[s]*,/;
#    my $__string = qq{
#        1) Name of the Municipal Corporation: Mumbai Manipurer Description:,
#        Other Information: Office premises area 8000 sq. Foot Built, 12th Floor,
#        Hectus House Building's, Venkatesh Premises Co.op.source, Plot No. 193,
#        Nariman Point, Block-3, Backbe Reclamation Mumbai - 400021 ..... along
#        with 3 covered car parking space 59,60,61 executed Deed of Transfer in
#        respect of the income. Due date of 07/09/2000 The total stamp duty paid
#        on the document is Rs. 1,33,24,200 / - Transfer from transfer deed is
#        12,53,00,000 / - Assessing no. ADJ / M / 173/2017 (CTS Number: 1949;))
#   };
#    $__string = cleanstring($__string);
#    print "$__string\n";
#    return ($__string, $__regex);
#}

# Name of\s*[the]*\s*Building[\s:\-]*([^,]+)

# ($string, $regex) = corporatepark();
# ($string, $regex) = migbuilding();
# ($string, $regex) = industrialestate();
# ($string, $regex) = buildingname();
# ($string, $regex) = plotnumber();
# ($string, $regex) = beforecoop();
# ($string, $regex) = buildingnameend();
($string, $regex) = testlookahead();

# if ($string =~ /[,]\s*([^,]*Park)[,]/i) {
print "$string\n";
print "$regex\n";
if ($string =~ /$regex/i) {
    print "Matched\n";
    print "$1\n";
} else {
    print "Not Matched";
}


# 1) Andheri
# Andheri