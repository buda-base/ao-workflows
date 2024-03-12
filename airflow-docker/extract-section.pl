#!/usr/bin/env perl
# Extract a section from a config file, where sections
# are marked by [section_name]

use strict;
use warnings;

my ($config_file, $section) = @ARGV;

open my $fh, '<', $config_file or die "Could not open '$config_file': $!";

my $in_section = 0;

# D'oh! I forgot to print the section header
print "[$section]\n";
while (my $line = <$fh>) {
    if ($line =~ /^\s*\[\Q$section\E\]\s*$/) {
        $in_section = 1;
    } elsif ($line =~ /^\s*\[.*\]\s*$/) {
        $in_section = 0;
    } elsif ($in_section) {
        print $line;
    }
}

close $fh;