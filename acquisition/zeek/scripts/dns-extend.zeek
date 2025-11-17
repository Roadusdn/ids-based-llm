module DNS;

export {
    redef record DNS::Info += {
        query_len: count &optional;
        qtype_name: string &optional;
    };
}

event dns_request(c: connection, msg: dns_msg, query: dns_query)
    {
    c$dns$query_len = |query$qname|;
    c$dns$qtype_name = DNS::qt_to_str(query$qtype);
    }

event dns_response(c: connection, msg: dns_msg, answer: dns_answer)
    {
    # (원한다면 A/AAAA/CNAME 등 추가 정보 확장 가능)
    }

