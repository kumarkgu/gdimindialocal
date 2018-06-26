use strict;
use warnings;
use Win32;
use Spreadsheet::Read qw(ReadData);
use Excel::Writer::XLSX;

my ($homepath, $projpath);
my @country = ("Sri_Lanka", "India");
my @filename;

sub setpaths {
    my $__name = Win32::LoginName;
    my $__proj = "Documents/JLL/Projects";
    my $__path = join "/", "C:/Users", $__name, $__proj;
    return $__path;
}

sub setfilename {
    my @country = @_;
    my $file_prefix = "Emergency_Contact_";
    my @filename;
    push (@filename, $file_prefix . $_ . ".xlsx") foreach (@country);
    return @filename;
}

sub splitNames {
    my ($__name) = @_;
    my @__result = "" x 5;
    $__result[0] = $__name;
    if ($__name =~ /^\d+[\+\-\/]*\d*/) {
        $__result[4] = "$__name is not a valid Name"
    } else {
        if ($__name =~ /^[^\s\.]+[\s\.]*$/) {
            $__result[1] = chomp($__name);
        } elsif ($__name =~ /^([^\s\.]+)([\s\.]+)([^\s\.]+)([\s\.]*)$/) {
            $__result[1] = chomp($1);
            $__result[3] = chomp($3);
        } elsif ($__name =~ /^([^\s\.]+)([\s\.]+)([^\s\.]+[\s\.]*.*)([\s\.]+)([^\s\.]+)([\s\.]*)$/) {
            $__result[1] = chomp($1);
            $__result[2] = chomp($3);
            $__result[3] = chomp($5);
        } else {
            print "No Match\n";
        }
    }
    return @__result;
}

sub splitNameArray {
    my ($__name) = @_;
    my @__aname = split($__name);
}

$projpath = setpaths();
@filename = setfilename(@country);
print ("$_\n") foreach (@filename);
my $name = "T.V.J Srikant";
my @name_split = splitNames($name);
print ("$_\n") foreach (@name_split);


