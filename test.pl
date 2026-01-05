#!/usr/bin/perl
use strict;
use warnings;
use LWP::UserAgent;

my $ua = LWP::UserAgent->new;
$ua->timeout(10);

my @urls = (
    'https://api.github.com/users/tiangolo',
    'https://api.github.com/users/encode',
);

foreach my $url (@urls) {
    my $response = $ua->get($url);
    if ($response->is_success) {
        print "Success: " . $response->status_line . "\n";
    } else {
        print "Failed: " . $response->status_line . "\n";
    }
}
