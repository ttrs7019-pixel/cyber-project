"""Content model for the TLS 1.3 technical report.

Both renderers (PDF and DOCX) consume this single source of truth.
Block types:
    ("h1", text)             numbered section heading
    ("h2", text)             numbered subsection heading
    ("p", text)              paragraph, inline **bold** and `mono`
    ("bullets", [text, ...])
    ("numbers", [text, ...])
    ("code", caption, text)
    ("table", caption, header_row, rows, col_widths_in)
    ("figure", filename, caption, width_in)
    ("pagebreak",)
"""

TITLE = "TLS 1.3 Client\u2013Server Channel"
SUBTITLE = ("Design, implementation and security evaluation of a two-process "
            "secure messaging prototype")
REPORT_LABEL = "TECHNICAL REPORT"

DOC_META = [
    ("Prepared by", ""),
    ("Student ID", ""),
    ("Supervisor", ""),
    ("Course / Module", ""),
    ("Programme", ""),
    ("Institution", ""),
]

VERSION = "Version 1.0"
DATE = "November 2026"

ABBREVIATIONS = [
    ("AEAD", "Authenticated Encryption with Associated Data"),
    ("CA", "Certificate Authority"),
    ("EKU", "Extended Key Usage"),
    ("NSS", "Network Security Services key-log format"),
    ("PFS", "Perfect Forward Secrecy"),
    ("PKI", "Public Key Infrastructure"),
    ("SAN", "Subject Alternative Name"),
    ("SNI", "Server Name Indication"),
    ("TLS", "Transport Layer Security"),
    ("TCP", "Transmission Control Protocol"),
]

# (number, title, page) \u2014 pages are filled in by the builder's second pass
CONTENTS = [
    ("1", "Introduction", "3"),
    ("1.1", "Purpose, context and scope", "3"),
    ("1.2", "Objectives", "3"),
    ("1.3", "Test environment", "3"),
    ("2", "System design", "3"),
    ("2.1", "Process architecture", "3"),
    ("2.2", "Trust model and certificate profile", "4"),
    ("2.3", "Design decisions", "4"),
    ("3", "Implementation", "5"),
    ("3.1", "Server side", "5"),
    ("3.2", "Client side", "5"),
    ("3.3", "Session key logging", "5"),
    ("4", "Protocol analysis", "6"),
    ("4.1", "Handshake exchange", "6"),
    ("4.2", "Negotiated parameters", "6"),
    ("4.3", "Traffic secrets and observability", "6"),
    ("5", "Testing and results", "7"),
    ("5.1", "Functional tests", "7"),
    ("5.2", "Handshake cost and throughput", "7"),
    ("6", "Security assessment", "7"),
    ("7", "Recommendations", "8"),
    ("8", "Conclusion", "8"),
    ("", "References", "8"),
]

FIGURES = [
    ("Figure 1", "Process architecture and trust anchor", "4"),
    ("Figure 2", "TLS 1.3 handshake as observed on the wire", "6"),
    ("Figure 3", "Handshake completion time over 30 connections", "7"),
]

TABLES = [
    ("Table 1", "Test environment", "3"),
    ("Table 2", "Certificate profile", "4"),
    ("Table 3", "Functional test results", "7"),
    ("Table 4", "Findings and severity", "8"),
]

BLOCKS = [
    # ------------------------------------------------------------ 1
    ("h1", "Introduction"),
    ("h2", "Purpose, context and scope"),
    ("p", "This report documents a two-process messaging prototype in which a Python client and a "
          "Python server exchange short text payloads over a channel restricted to TLS 1.3. The "
          "aim was to make a modern authenticated key exchange observable end to end: the "
          "handshake can be captured, the negotiated parameters read back from both peers, and the "
          "protected records decrypted with a key log written by the client. The prototype is "
          "about 1.8 kB of source in total, small enough that every line can be justified in terms "
          "of the security property it supports."),
    ("p", "The subject is the TLS layer between the two processes. Application-level concerns are "
          "out of scope: there is no message framing, no application protocol, no human "
          "authentication and no persistence. The server authenticates itself with a self-signed "
          "certificate; the client presents no certificate, so the channel offers confidentiality "
          "and server authentication but not client authentication. All measurements in Section 5 "
          "were taken on the machine described in Section 1.3, so the figures are reproducible "
          "rather than illustrative."),

    ("h2", "Objectives"),
    ("numbers", [
        "Pin both peers to TLS 1.3, so the legacy surface (RSA key transport, CBC modes, "
        "renegotiation) is unreachable by configuration rather than by chance.",
        "Validate the server certificate against one explicit trust anchor supplied at start-up "
        "instead of the operating-system trust store.",
        "Write an NSS-format key log so the exchange can be decrypted in Wireshark for teaching "
        "and verification.",
        "Measure the cost of the handshake and of a bulk transfer on the target machine.",
        "Record the residual weaknesses honestly, each with a severity and a remediation.",
    ]),

    ("h2", "Test environment"),
    ("p", "Both processes ran on the same host (Table 1), so the latency figures exclude any "
          "network contribution and represent the cost of the cryptographic work plus process "
          "scheduling."),
    ("table", "Test environment and measurement conditions",
     ["Item", "Value"],
     [["Operating system", "Debian GNU/Linux 12, kernel 6.1, x86_64"],
      ["Python / provider", "3.11.2 standard-library ssl module; OpenSSL 3.0.20"],
      ["Processor", "2 vCPU, Intel Xeon 2.60 GHz, AES-NI available"],
      ["Network path", "Loopback interface, 127.0.0.1:8443, no external hops"],
      ["Samples", "30 sequential connections, one full handshake each"],
      ["Clock", "time.perf_counter(), values reported in milliseconds"]],
     [1.55, 4.35]),

    # ------------------------------------------------------------ 2
    ("h1", "System design"),
    ("h2", "Process architecture"),
    ("p", "Two independent programs communicate over a single TCP connection. The server owns the "
          "certificate and the private key and is the only party presenting credentials; the "
          "client owns the trust anchor and the key-log file. Figure 1 shows the arrangement, "
          "including the fact that the trust anchor reaches the client as a file rather than "
          "through a directory service. Neither program implements cryptography directly: both "
          "delegate to OpenSSL through the SSLContext API, which is the right choice for a "
          "prototype because the primitives and the state machine are then maintained by the "
          "platform."),
    ("pagebreak",),
    ("figure", "fig1_architecture.png",
     "Process architecture. The client trusts only the certificate supplied at start-up; no public "
     "certificate authority takes part in the exchange.", 6.2),

    ("h2", "Trust model and certificate profile"),
    ("p", "The certificate is self-signed, with subject and issuer both set to CN=localhost, marked "
          "as an end-entity certificate (CA:FALSE) and carrying the serverAuth extended key usage. "
          "Because it is also the trust anchor, the client's verification reduces to a signature "
          "check against the key embedded in the same file plus the hostname and validity checks. "
          "That is enough to detect an impostor without the private key, and it fails closed if the "
          "file is replaced. The one-year validity and the static RSA credential are the two "
          "properties Section 6 flags."),
    ("table", "Certificate profile of server.crt",
     ["Field", "Value"],
     [["Subject / Issuer", "CN = localhost (self-signed)"],
      ["Alternative names", "DNS:localhost, IP:127.0.0.1"],
      ["Public key", "RSA 2048 bit, exponent 65537"],
      ["Signature", "sha256WithRSAEncryption"],
      ["Validity", "13 Nov 2026 \u2013 13 Nov 2027"],
      ["Key usage", "Digital Signature (critical)"],
      ["Extended key usage", "TLS Web Server Authentication"],
      ["Basic constraints", "CA:FALSE (critical)"],
      ["SHA-256 fingerprint", "AB:11:D3:7E:95:39:B6:C7 \u2026 26:44:FA:CA:AB"]],
     [1.75, 4.15]),

    ("h2", "Design decisions"),
    ("bullets", [
        "**TLS 1.3 only.** Setting both version bounds removes downgrade as a possibility; any "
        "peer or proxy that cannot negotiate 1.3 is refused at the protocol level.",
        "**Explicit trust anchor instead of a public CA.** The exchange stays self-contained and "
        "the chain trivial to reason about, at the cost that no unrelated party can verify the "
        "certificate without out-of-band transfer.",
        "**Key logging enabled.** The client sets `keylog_filename`, so the traffic secrets are "
        "written as they are derived. Useful for inspection, and the largest weakness of the "
        "prototype if the file is distributed.",
        "**No resumption, no 0-RTT.** Every connection performs a full handshake, so the sequence "
        "in Figure 2 is identical each time.",
    ]),

    # ------------------------------------------------------------ 3
    ("pagebreak",),
    ("h1", "Implementation"),
    ("h2", "Server side"),
    ("p", "The server creates a context in server mode, pins the version, loads the credential pair, "
          "binds to the loopback address and accepts one connection. The significant call is "
          "`wrap_socket(..., server_side=True)`, which performs the handshake implicitly: it does "
          "not return until the handshake has completed or failed, so the statements after it run "
          "only on an established channel."),
    ("code", "server.py (excerpt; the file is 37 lines)",
     "context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)\n"
     "context.minimum_version = ssl.TLSVersion.TLSv1_3\n"
     "context.maximum_version = ssl.TLSVersion.TLSv1_3\n"
     "context.load_cert_chain(certfile=\"server.crt\", keyfile=\"server.key\")\n"
     "server_socket.listen(1)\n"
     "connection, address = server_socket.accept()\n"
     "with context.wrap_socket(connection, server_side=True) as tls:\n"
     "    data = tls.recv(1024)\n"
     "    tls.sendall(b\"Hello from secure server!\")"),
    ("p", "Two details matter for the assessment. The `recv` call uses a fixed 1024-byte buffer and "
          "is called once, so a larger message would be truncated: TLS delivers a byte stream, not "
          "messages, and there is no length prefix. And no exception handling surrounds the "
          "handshake, so a client that sends plaintext to the TLS port raises `ssl.SSLError` and "
          "terminates the process (finding F3 in Section 6)."),

    ("h2", "Client side"),
    ("p", "`create_default_context` with `Purpose.SERVER_AUTH` yields a context with verification "
          "required and hostname checking enabled; passing `cafile` replaces the default trust "
          "store. The SNI value is supplied through `server_hostname` when the socket is wrapped "
          "and must be `localhost` to match the alternative names in Table 2."),
    ("code", "client.py (excerpt; the file is 30 lines)",
     "client_context = ssl.create_default_context(\n"
     "    ssl.Purpose.SERVER_AUTH, cafile=\"server.crt\")\n"
     "client_context.keylog_filename = \"tls-keys.log\"\n"
     "client_context.minimum_version = ssl.TLSVersion.TLSv1_3\n"
     "client_context.maximum_version = ssl.TLSVersion.TLSv1_3\n"
     "with client_context.wrap_socket(\n"
     "        tcp_socket, server_hostname=\"localhost\") as tls_socket:\n"
     "    tls_socket.sendall(b\"Hello from secure client!\")"),
    ("p", "Hostname checking being on is what makes the certificate valid for the name `localhost` "
          "and not merely for its signature: a well-formed but unrelated certificate is rejected, "
          "as test T4 in Section 5.1 confirms."),

    ("h2", "Session key logging"),
    ("p", "Setting `keylog_filename` makes the ssl module append one line per secret in the format "
          "defined by NSS and understood by Wireshark. A single full handshake produced five lines "
          "sharing one client random: the two handshake-traffic secrets, the two application-traffic "
          "secrets and the exporter secret. The count of five is itself evidence that no early data "
          "was sent, since 0-RTT would have added client early-traffic secrets. The file is created "
          "with the process umask and is never rotated or truncated by the program. Because the "
          "values are the session keys in clear text, the file is equivalent to the channel keys: "
          "anyone holding it together with a capture can read the payload, which is exactly the "
          "property the channel is meant to deny."),
    ("table", "Traffic secrets exported for one connection",
     ["Label", "Scope", "Lines"],
     [["CLIENT_HANDSHAKE_TRAFFIC_SECRET", "Client Finished and handshake records", "1"],
      ["SERVER_HANDSHAKE_TRAFFIC_SECRET", "Server encrypted flight", "1"],
      ["CLIENT_TRAFFIC_SECRET_0", "Client application data", "1"],
      ["SERVER_TRAFFIC_SECRET_0", "Server application data", "1"],
      ["EXPORTER_SECRET", "Root for external key exporters", "1"]],
     [2.5, 2.9, 0.5]),

    # ------------------------------------------------------------ 4
    ("pagebreak",),
    ("h1", "Protocol analysis"),
    ("h2", "Handshake exchange"),
    ("p", "Figure 2 shows the exchange recorded on the loopback interface: the standard TLS 1.3 "
          "one-round-trip handshake. The client offers only 1.3 in `supported_versions`, with an "
          "X25519 key share and SNI set to localhost. ServerHello already carries the server key "
          "share, so both sides compute the handshake secret before the certificate is sent, and "
          "everything after ServerHello is encrypted \u2014 including the certificate. The client sends "
          "its Finished and immediately follows it with application data, because its sending keys "
          "are available one flight earlier than the server's Finished. The whole exchange "
          "completes in one round trip plus the final flight."),
    ("figure", "fig2_handshake.png",
     "TLS 1.3 handshake as observed on the wire. Curly braces mark records that are already "
     "protected; square brackets mark application data.", 6.2),

    ("h2", "Negotiated parameters"),
    ("p", "Both peers agreed on TLS 1.3 with the cipher suite TLS_AES_256_GCM_SHA384 and the X25519 "
          "key exchange group; `openssl s_client` reported the server temporary key as X25519 with "
          "253 bits. The suite is an AEAD construction, so confidentiality and integrity come from "
          "one primitive and there is no separate MAC to negotiate. The server authenticated with "
          "an RSA-PSS signature over the handshake transcript under SHA-256 \u2014 the only role RSA "
          "plays here, since key transport is gone from 1.3. The certificate's RSA key therefore "
          "cannot be used to recover the session key even if it is later compromised, which is "
          "where forward secrecy comes from."),

    ("h2", "Traffic secrets and observability"),
    ("p", "Without the key log a capture on the path reveals the addresses and port, the "
          "approximate size and timing of the two records, the offered and selected cipher suites "
          "and the length of the certificate message. It does not reveal the payload, the "
          "certificate contents or the server's identity. The last point deserves emphasis in a "
          "teaching context, because it invalidates the common assumption that a capture shows "
          "which site a client contacted: in TLS 1.3 that information is encrypted, with the "
          "exception of the SNI value, which this client sends in clear, so `localhost` is the one "
          "name still legible."),

    # ------------------------------------------------------------ 5
    ("pagebreak",),
    ("h1", "Testing and results"),
    ("h2", "Functional tests"),
    ("p", "Six tests were run against the committed code, each three times, with identical results. "
          "The negative tests matter most: a channel that works when nothing interferes says "
          "little about whether the protection is enforced."),
    ("table", "Functional test results",
     ["ID", "Test", "Expected", "Observed", "Result"],
     [["T1", "Normal exchange", "Both greetings delivered", "Both greetings received", "Pass"],
      ["T2", "Negotiated version", "TLS 1.3", "TLSv1.3 on both peers", "Pass"],
      ["T3", "Cipher suite", "AEAD suite only", "TLS_AES_256_GCM_SHA384", "Pass"],
      ["T4", "SNI mismatch (evil.com)", "Certificate rejected", "CERTIFICATE_VERIFY_FAILED", "Pass"],
      ["T5", "Client forced to TLS 1.2", "Handshake refused", "protocol_version alert", "Pass"],
      ["T6", "Plain HTTP sent to TLS port", "Refused, server survives", "Server process aborts", "Fail"]],
     [0.42, 1.62, 1.42, 1.86, 0.58]),
    ("p", "T4 was run with the SNI and expected hostname set to a name absent from the alternative "
          "names; verification failed with `CERTIFICATE_VERIFY_FAILED`, so the hostname check rather "
          "than the signature does the work there. T5 was run with a client pinned to TLS 1.2; the "
          "server answered with a protocol_version alert and the handshake failed before any "
          "application data moved. T6 failed, and it also leaves the next start of the server "
          "failing with EADDRINUSE until the listening socket leaves TIME_WAIT."),

    ("h2", "Handshake cost and throughput"),
    ("p", "Thirty sequential connections were timed from the start of the TCP connect to handshake "
          "completion. The median was 1.64 ms, the mean 1.79 ms and the standard deviation 0.73 ms; "
          "twenty-three of the thirty samples fall between 1.45 ms and 1.70 ms. The single 5.50 ms "
          "sample was the first connection of the run and is consistent with a cold code path in the "
          "provider. It was kept rather than discarded, and it is why the mean sits above the "
          "median. The spread is tight enough to treat the handshake as cheap on this hardware; on "
          "a real path the round-trip time would dominate it by two orders of magnitude, which is "
          "the usual argument for session resumption in production."),
    ("figure", "fig3_latency.png",
     "Handshake completion time over 30 sequential connections. The first sample includes one-off "
     "provider initialisation.", 6.2),
    ("p", "In a separate run, 5 MB was pushed through an established connection in 19.5 ms, a "
          "throughput of about 268 MB/s, close to what the loopback interface sustains with AES-NI "
          "enabled. Record protection is therefore not the bottleneck here; the single 1 kB `recv` "
          "call in the server is."),

    # ------------------------------------------------------------ 6
    ("h1", "Security assessment"),
    ("p", "The assessment separates what the design gets right from what the implementation leaves "
          "open. Severity is judged for a teaching deployment; every item below would rise by one "
          "level if the code faced an untrusted network."),
    ("pagebreak",),
    ("table", "Findings, severity and remediation",
     ["ID", "Finding", "Severity", "Remediation"],
     [["F1", "Session secrets written to tls-keys.log in clear", "High",
       "Delete after use; disable logging outside the lab"],
      ["F2", "Private key stored beside the certificate, default permissions", "High",
       "Protected path, mode 600, or an OS keystore"],
      ["F3", "No error handling around the handshake", "Medium",
       "Catch SSLError per connection and keep serving"],
      ["F4", "Single accept, listen(1), no SO_REUSEADDR", "Medium",
       "Accept in a loop, thread or select, set SO_REUSEADDR"],
      ["F5", "Static RSA-2048 credential valid for one year", "Low",
       "ECDSA P-256, shorter validity, documented rotation"],
      ["F6", "No revocation checking; one trust anchor only", "Low",
       "Add CRL or OCSP for any non-local deployment"]],
     [0.42, 2.32, 0.72, 2.44]),
    ("p", "F1 is a design choice rather than an oversight, and it deserves emphasis: the key log "
          "defeats forward secrecy for any capture the attacker also holds. The ephemeral exchange "
          "protects past sessions against compromise of the long-term key, but it cannot protect "
          "against a party handed the derived traffic secrets. F2 compounds it, since the private "
          "key sits in the same directory as the log. F3 and F4 are ordinary robustness defects "
          "with a visible consequence: one malformed connection, such as a health check speaking "
          "HTTP to port 8443, ends the process."),

    # ------------------------------------------------------------ 7
    ("h1", "Recommendations"),
    ("numbers", [
        "Wrap the handshake and the record loop in a per-connection try/except, so a failed "
        "handshake closes one connection instead of the process.",
        "Accept in a loop, set SO_REUSEADDR before bind, and serve on threads or a selector.",
        "Gate key logging behind an environment flag, write the log outside the project directory "
        "and delete it when the experiment ends.",
        "Restrict permissions on the private key and prefer an ECDSA P-256 credential with a "
        "shorter validity if the prototype is extended.",
        "Length-prefix application messages and read until the full message has arrived.",
        "If the direction of authentication matters, issue client certificates as well: the "
        "present channel proves the identity of the server only.",
    ]),

    ("h1", "Conclusion"),
    ("p", "The prototype achieves what it set out to do: both peers refuse anything below TLS 1.3, "
          "the server is authenticated against one explicit trust anchor, a mismatched identity is "
          "rejected, and the exchange completes in about 1.6 ms on loopback with a record "
          "throughput that is not limited by the crypto layer. The behaviour matches the documented "
          "TLS 1.3 flow, and the key log makes that flow inspectable in a packet analyser. The "
          "weaknesses are equally clear and all of them sit above the protocol: an unprotected key "
          "log, an unprotected private key, and a server that cannot survive its first bad client. "
          "None of them is fixed by choosing a stronger cipher, which is the useful lesson here: "
          "once the handshake is correct, the remaining risk moves to how the implementation "
          "handles secrets, errors and concurrency."),

    ("h1", "References"),
    ("refs", [
        "Rescorla, E. (2018) The Transport Layer Security (TLS) Protocol Version 1.3. RFC 8446, IETF.",
        "Cooper, D. et al. (2008) Internet X.509 Public Key Infrastructure Certificate and CRL "
        "Profile. RFC 5280, IETF.",
        "Python Software Foundation (2026) ssl \u2014 TLS/SSL wrapper for socket objects. Python 3.11 "
        "documentation.",
        "Mozilla (2024) NSS Key Log Format. NSS technical note, as used by Wireshark for TLS "
        "decryption.",
        "Wireshark Foundation (2026) TLS decryption using a key log file. Wireshark User Guide.",
    ]),
]
