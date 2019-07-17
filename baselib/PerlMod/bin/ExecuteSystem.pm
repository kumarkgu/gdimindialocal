package PerlMod::bin::ExecuteSystem;
use strict;
use warnings FATAL => 'all';
use IPC::Run3;

sub ExecCommand {
    my @command = @_;
    my ($stdout, $stderr);
    eval { run3(\@command, \undef, \$stdout, \$stderr) };
    if ($@) {
        print "Error: $@";
    } elsif ($? & 0x7F) {
        say "Killed by signal ".($? & 0x7F);
    } elsif ($? >> 8) {
        say "Exited with error ".($? >> 8);
    } else {
        print "$stdout";
        say "Completed Successfully";
    }
}

1;