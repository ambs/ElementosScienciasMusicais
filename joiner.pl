#!/usr/bin/env perl

use v5.38;

use Path::Tiny;

my $all = "";

my @files = path("pages")->children( qr/\d+\.md/ );
foreach my $file (sort @files) {
    my $content = $file->slurp_utf8;
    unless ($all =~ s/\.\.\.\s*$/$content/) {
        $all .= "\n\n$content";
    }
}
    

path("all.md")->spew_utf8($all);
