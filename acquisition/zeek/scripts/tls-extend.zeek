module SSL;

export {
    redef record SSL::Info += {
        ja3_hash: string &optional;
    };
}

event ssl_client_hello(c: connection)
    {
    if ( c$ssl?$client_hello && c$ssl?$client_hello$ja3 )
        c$ssl$ja3_hash = c$ssl$client_hello$ja3;
    }

