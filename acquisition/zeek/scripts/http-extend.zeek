module HTTP;

export {
    redef record HTTP::Info += {
        user_agent: string &optional;
        uri: string &optional;
    };
}

event http_request(c: connection, method: string, original_URI: string)
    {
    c$http$user_agent = c$http$user_agent ? c$http$user_agent : "";
    c$http$uri = original_URI;
    }

event http_header(c: connection, is_orig: bool, name: string, value: string)
    {
    if ( is_orig && name == "user-agent" )
        c$http$user_agent = value;
    }
