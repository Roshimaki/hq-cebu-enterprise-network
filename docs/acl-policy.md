# ACL Policy

This document lists every access control list (ACL) written for the HQ–CEBU network, where each one is applied, and its status. The policy summary is in the [README](../README.md#7-security).

**Principle:** least privilege. Each VLAN can start connections only to the destinations its function requires. Everything else internal is denied. Users keep internet access, except Voice and Server.

---

## Design rules

1. **Direction and placement.** ACLs are applied **inbound on the SVI of the VLAN that starts the traffic**, on **both switches** of the HSRP pair, so the policy still applies after a failover.
2. **Order matters.** The first matching line wins, so every ACL follows the same order:
   1. DHCP (the distribution switch is the DHCP server, so discover packets hit the SVI)
   2. Replies to connections that others started (`established` and `echo-reply`)
   3. Allowed internal destinations
   4. Deny all other internal ranges
   5. Permit internet
3. **ACLs are stateless.** `established` matches TCP packets with ACK or RST set, which are replies. A new connection starts with a plain SYN and is dropped. UDP has no equivalent, so UDP replies need a rule by port (DNS 53, NTP 123), or they are dropped.
4. **Asymmetric by design.** IT can start connections to every VLAN, but no VLAN can start a connection to IT. Replies to IT pass because of the reply lines in rule 2.
5. **Packet Tracer limitations.** The `log` keyword is not accepted, so none of these ACLs use it. The `show access-lists <name>` match counters are used as evidence instead.
6. **IT VLANs have no ACL.** An ACL that permits everything has no effect. IT is protected on the devices themselves through the SSH `SSH-ALLOW` access-class.

### Wildcard masks used

| Prefix | Wildcard |
|---|---|
| /26 | 0.0.0.63 |
| /27 | 0.0.0.31 |
| /28 | 0.0.0.15 |
| /29 | 0.0.0.7 |

---

## Where each ACL is applied

| ACL | VLAN | Applied on | Allowed to start connections to | Internet | Configured | Tested |
|---|---|---|---|---|---|---|
| `MANAGEMENT-IN` | HQ 10 | HQ-DIST-SWT1, SWT2 | Server, Sales, HR, Finance, Support, Engineering, Operations, CEBU Management | Yes | TODO | TODO |
| `SALES-IN` | HQ 20 | HQ-DIST-SWT1, SWT2 | Server, Support | Yes | TODO | TODO |
| `GUEST-IN` | HQ 30 | HQ-DIST-SWT1, SWT2 | None | Yes | TODO | ✅ |
| none | HQ 40 (IT) | n/a | Everything | Yes | n/a | n/a |
| `SERVER-IN` | HQ 50 | HQ-DIST-SWT3, SWT4 | None (replies only) | No | TODO | TODO |
| `HR-IN` | HQ 60 | HQ-DIST-SWT3, SWT4 | Server | Yes | TODO | TODO |
| `FINANCE-IN` | HQ 70 | HQ-DIST-SWT3, SWT4 | Server | Yes | TODO | TODO |
| `VOICE-IN` | HQ 80 | HQ-DIST-SWT3, SWT4 | CEBU Voice; CME syslog and NTP to Server | No | TODO | TODO |
| `SUPPORT-IN` | HQ 90 | HQ-DIST-SWT3, SWT4 | Server, Sales | Yes | TODO | TODO |
| `ENGINEERING-IN` | HQ 100 | HQ-DIST-SWT5, SWT6 | Server, Operations | Yes | TODO | TODO |
| `OPERATIONS-IN` | HQ 110 | HQ-DIST-SWT5, SWT6 | Server, Engineering | Yes | TODO | TODO |
| `CEBU-MGMT-IN` | CEBU 210 | CEBU-DIST-SWT1, SWT2 | CEBU Sales, CEBU IT, HQ Server, HQ Management | Yes | Applied (not shown in PT running-config) | TODO |
| `GUEST-IN` | CEBU 220 | CEBU-DIST-SWT1, SWT2 | None | Yes | Applied (not shown in PT running-config) | ✅ |
| none | CEBU 230 (IT) | n/a | Everything | Yes | n/a | n/a |
| `CEBU-VOICE-IN` | CEBU 240 | CEBU-DIST-SWT1, SWT2 | HQ Voice; CME syslog and NTP to Server | No | Applied (not shown in PT running-config) | TODO |
| `CEBU-SALES-IN` | CEBU 250 | CEBU-DIST-SWT1, SWT2 | HQ Server | Yes | Applied (not shown in PT running-config) | TODO |

> **Packet Tracer note:** the multilayer switch applies `ip access-group` on an SVI but does not show it in `show running-config`. Verify with the `show access-lists <name>` match counters and keep the screenshots under `docs/images/`. Update the **Configured** and **Tested** columns to match what you deployed and verified.

---

## HQ

### Management (VLAN 10, 192.168.10.0/27)

```
ip access-list extended MANAGEMENT-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.10.0 0.0.0.31 eq bootpc any eq bootps
 remark replies to connections that others started (IT, CEBU Management)
 permit tcp 192.168.10.0 0.0.0.31 any established
 permit icmp 192.168.10.0 0.0.0.31 any echo-reply
 remark allowed destinations
 permit ip 192.168.10.0 0.0.0.31 192.168.50.0 0.0.0.7
 permit ip 192.168.10.0 0.0.0.31 192.168.20.0 0.0.0.63
 permit ip 192.168.10.0 0.0.0.31 192.168.70.0 0.0.0.63
 permit ip 192.168.10.0 0.0.0.31 192.168.90.0 0.0.0.63
 permit ip 192.168.10.0 0.0.0.31 192.168.100.0 0.0.0.63
 permit ip 192.168.10.0 0.0.0.31 192.168.110.0 0.0.0.63
 permit ip 192.168.10.0 0.0.0.31 192.168.60.0 0.0.0.31
 permit ip 192.168.10.0 0.0.0.31 192.168.210.0 0.0.0.15
 remark everything else internal is denied (IT, Voice, Guest, VLAN 900)
 deny ip 192.168.10.0 0.0.0.31 192.168.0.0 0.0.255.255
 deny ip 192.168.10.0 0.0.0.31 10.0.0.0 0.255.255.255
 deny ip 192.168.10.0 0.0.0.31 172.16.0.0 0.15.255.255
 deny ip 192.168.10.0 0.0.0.31 1.1.1.0 0.0.0.255
 deny ip 192.168.10.0 0.0.0.31 2.2.2.0 0.0.0.255
 deny ip 192.168.10.0 0.0.0.31 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.10.0 0.0.0.31 any
!
interface vlan 10
 ip access-group MANAGEMENT-IN in
```

### Sales (VLAN 20, 192.168.20.0/26)

```
ip access-list extended SALES-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.20.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.20.0 0.0.0.63 any established
 permit icmp 192.168.20.0 0.0.0.63 any echo-reply
 remark allowed destinations: Server and Support
 permit ip 192.168.20.0 0.0.0.63 192.168.50.0 0.0.0.7
 permit ip 192.168.20.0 0.0.0.63 192.168.90.0 0.0.0.63
 remark everything else internal is denied
 deny ip 192.168.20.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.20.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.20.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.20.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.20.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.20.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.20.0 0.0.0.63 any
!
interface vlan 20
 ip access-group SALES-IN in
```

### Guest (VLAN 30, 192.168.30.0/28)

```
ip access-list extended GUEST-IN
 remark allow DHCP (discover and renew)
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.30.0 0.0.0.15 eq bootpc any eq bootps
 remark replies to connections that IT started
 permit tcp 192.168.30.0 0.0.0.15 any established
 permit icmp 192.168.30.0 0.0.0.15 any echo-reply
 remark block HQ guest from all internal networks
 deny ip 192.168.30.0 0.0.0.15 10.0.0.0 0.255.255.255
 deny ip 192.168.30.0 0.0.0.15 172.16.0.0 0.15.255.255
 deny ip 192.168.30.0 0.0.0.15 192.168.0.0 0.0.255.255
 remark block device loopbacks
 deny ip 192.168.30.0 0.0.0.15 1.1.1.0 0.0.0.255
 deny ip 192.168.30.0 0.0.0.15 2.2.2.0 0.0.0.255
 remark block tunnel and ISP addressing
 deny ip 192.168.30.0 0.0.0.15 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.30.0 0.0.0.15 any
!
interface vlan 30
 ip access-group GUEST-IN in
```

### Server (VLAN 50, 192.168.50.0/29)

The server only answers requests. It never starts a connection. Syslog, NTP requests and SNMP traps flow *toward* the server, so they never match this ACL. If the server later forwards DNS to 8.8.8.8, add a `permit` for it before the final `deny`.

```
ip access-list extended SERVER-IN
 remark TCP replies
 permit tcp 192.168.50.0 0.0.0.7 any established
 remark DNS and NTP replies
 permit udp 192.168.50.0 0.0.0.7 eq 53 any
 permit udp 192.168.50.0 0.0.0.7 eq 123 any
 remark ping replies
 permit icmp 192.168.50.0 0.0.0.7 any echo-reply
 remark block anything else the server starts
 deny ip 192.168.50.0 0.0.0.7 any
!
interface vlan 50
 ip access-group SERVER-IN in
```

### HR (VLAN 60, 192.168.60.0/27)

```
ip access-list extended HR-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.60.0 0.0.0.31 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.60.0 0.0.0.31 any established
 permit icmp 192.168.60.0 0.0.0.31 any echo-reply
 remark allowed destination: Server only
 permit ip 192.168.60.0 0.0.0.31 192.168.50.0 0.0.0.7
 remark everything else internal is denied
 deny ip 192.168.60.0 0.0.0.31 192.168.0.0 0.0.255.255
 deny ip 192.168.60.0 0.0.0.31 10.0.0.0 0.255.255.255
 deny ip 192.168.60.0 0.0.0.31 172.16.0.0 0.15.255.255
 deny ip 192.168.60.0 0.0.0.31 1.1.1.0 0.0.0.255
 deny ip 192.168.60.0 0.0.0.31 2.2.2.0 0.0.0.255
 deny ip 192.168.60.0 0.0.0.31 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.60.0 0.0.0.31 any
!
interface vlan 60
 ip access-group HR-IN in
```

### Finance (VLAN 70, 192.168.70.0/26)

```
ip access-list extended FINANCE-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.70.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.70.0 0.0.0.63 any established
 permit icmp 192.168.70.0 0.0.0.63 any echo-reply
 remark allowed destination: Server only
 permit ip 192.168.70.0 0.0.0.63 192.168.50.0 0.0.0.7
 remark everything else internal is denied
 deny ip 192.168.70.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.70.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.70.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.70.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.70.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.70.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.70.0 0.0.0.63 any
!
interface vlan 70
 ip access-group FINANCE-IN in
```

### Voice (VLAN 80, 192.168.80.0/26)

Phones and CME share the VLAN, so traffic inside it never reaches the SVI. Only inter-site calls, CME logging and NTP, and replies to IT cross it. Voice has no internet access and no DHCP rule, because HQ-CME1 serves DHCP inside the VLAN.

```
ip access-list extended VOICE-IN
 remark replies to connections that IT started (SSH to CME, ping)
 permit tcp 192.168.80.0 0.0.0.63 any established
 permit icmp 192.168.80.0 0.0.0.63 any echo-reply
 remark inter-site calls to CEBU voice
 permit ip 192.168.80.0 0.0.0.63 192.168.240.0 0.0.0.63
 remark CME syslog and NTP to the server
 permit udp host 192.168.80.4 host 192.168.50.4 eq 514
 permit udp host 192.168.80.4 host 192.168.50.4 eq 123
 remark everything else is denied (no internet for voice)
 deny ip 192.168.80.0 0.0.0.63 any
!
interface vlan 80
 ip access-group VOICE-IN in
```

### Customer Support (VLAN 90, 192.168.90.0/26)

```
ip access-list extended SUPPORT-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.90.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.90.0 0.0.0.63 any established
 permit icmp 192.168.90.0 0.0.0.63 any echo-reply
 remark allowed destinations: Server and Sales
 permit ip 192.168.90.0 0.0.0.63 192.168.50.0 0.0.0.7
 permit ip 192.168.90.0 0.0.0.63 192.168.20.0 0.0.0.63
 remark everything else internal is denied
 deny ip 192.168.90.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.90.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.90.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.90.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.90.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.90.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.90.0 0.0.0.63 any
!
interface vlan 90
 ip access-group SUPPORT-IN in
```

### Engineering (VLAN 100, 192.168.100.0/26)

```
ip access-list extended ENGINEERING-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.100.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.100.0 0.0.0.63 any established
 permit icmp 192.168.100.0 0.0.0.63 any echo-reply
 remark allowed destinations: Server and Operations
 permit ip 192.168.100.0 0.0.0.63 192.168.50.0 0.0.0.7
 permit ip 192.168.100.0 0.0.0.63 192.168.110.0 0.0.0.63
 remark everything else internal is denied
 deny ip 192.168.100.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.100.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.100.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.100.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.100.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.100.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.100.0 0.0.0.63 any
!
interface vlan 100
 ip access-group ENGINEERING-IN in
```

### Operations (VLAN 110, 192.168.110.0/26)

```
ip access-list extended OPERATIONS-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.110.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (IT, Management)
 permit tcp 192.168.110.0 0.0.0.63 any established
 permit icmp 192.168.110.0 0.0.0.63 any echo-reply
 remark allowed destinations: Server and Engineering
 permit ip 192.168.110.0 0.0.0.63 192.168.50.0 0.0.0.7
 permit ip 192.168.110.0 0.0.0.63 192.168.100.0 0.0.0.63
 remark everything else internal is denied
 deny ip 192.168.110.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.110.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.110.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.110.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.110.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.110.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.110.0 0.0.0.63 any
!
interface vlan 110
 ip access-group OPERATIONS-IN in
```

---

## CEBU

### Management (VLAN 210, 192.168.210.0/28)

```
ip access-list extended CEBU-MGMT-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.210.0 0.0.0.15 eq bootpc any eq bootps
 remark replies to connections that others started (CEBU IT, HQ IT)
 permit tcp 192.168.210.0 0.0.0.15 any established
 permit icmp 192.168.210.0 0.0.0.15 any echo-reply
 remark allowed: CEBU Sales, CEBU IT, HQ Server, HQ Management
 permit ip 192.168.210.0 0.0.0.15 192.168.250.0 0.0.0.63
 permit ip 192.168.210.0 0.0.0.15 192.168.230.0 0.0.0.15
 permit ip 192.168.210.0 0.0.0.15 192.168.50.0 0.0.0.7
 permit ip 192.168.210.0 0.0.0.15 192.168.10.0 0.0.0.31
 remark everything else internal is denied (Voice, Guest, VLAN 900)
 deny ip 192.168.210.0 0.0.0.15 192.168.0.0 0.0.255.255
 deny ip 192.168.210.0 0.0.0.15 10.0.0.0 0.255.255.255
 deny ip 192.168.210.0 0.0.0.15 172.16.0.0 0.15.255.255
 deny ip 192.168.210.0 0.0.0.15 1.1.1.0 0.0.0.255
 deny ip 192.168.210.0 0.0.0.15 2.2.2.0 0.0.0.255
 deny ip 192.168.210.0 0.0.0.15 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.210.0 0.0.0.15 any
!
interface vlan 210
 ip access-group CEBU-MGMT-IN in
```

### Guest (VLAN 220, 192.168.220.0/28)

```
ip access-list extended GUEST-IN
 remark allow DHCP (discover and renew)
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.220.0 0.0.0.15 eq bootpc any eq bootps
 remark replies to connections that IT started
 permit tcp 192.168.220.0 0.0.0.15 any established
 permit icmp 192.168.220.0 0.0.0.15 any echo-reply
 remark block CEBU guest from all internal networks
 deny ip 192.168.220.0 0.0.0.15 10.0.0.0 0.255.255.255
 deny ip 192.168.220.0 0.0.0.15 172.16.0.0 0.15.255.255
 deny ip 192.168.220.0 0.0.0.15 192.168.0.0 0.0.255.255
 remark block device loopbacks
 deny ip 192.168.220.0 0.0.0.15 1.1.1.0 0.0.0.255
 deny ip 192.168.220.0 0.0.0.15 2.2.2.0 0.0.0.255
 remark block tunnel and ISP addressing
 deny ip 192.168.220.0 0.0.0.15 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.220.0 0.0.0.15 any
!
interface vlan 220
 ip access-group GUEST-IN in
```

### Voice (VLAN 240, 192.168.240.0/26)

```
ip access-list extended CEBU-VOICE-IN
 remark replies to connections that IT started (SSH to CME, ping)
 permit tcp 192.168.240.0 0.0.0.63 any established
 permit icmp 192.168.240.0 0.0.0.63 any echo-reply
 remark inter-site calls to HQ voice
 permit ip 192.168.240.0 0.0.0.63 192.168.80.0 0.0.0.63
 remark CME syslog and NTP to the HQ server
 permit udp host 192.168.240.4 host 192.168.50.4 eq 514
 permit udp host 192.168.240.4 host 192.168.50.4 eq 123
 remark everything else is denied (no internet for voice)
 deny ip 192.168.240.0 0.0.0.63 any
!
interface vlan 240
 ip access-group CEBU-VOICE-IN in
```

### Sales (VLAN 250, 192.168.250.0/26)

```
ip access-list extended CEBU-SALES-IN
 remark DHCP discover and renew
 permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps
 permit udp 192.168.250.0 0.0.0.63 eq bootpc any eq bootps
 remark replies to connections that others started (CEBU IT, HQ IT, CEBU Management)
 permit tcp 192.168.250.0 0.0.0.63 any established
 permit icmp 192.168.250.0 0.0.0.63 any echo-reply
 remark allowed destination: HQ Server only
 permit ip 192.168.250.0 0.0.0.63 192.168.50.0 0.0.0.7
 remark everything else internal is denied (IT, Management, Voice, Guest)
 deny ip 192.168.250.0 0.0.0.63 192.168.0.0 0.0.255.255
 deny ip 192.168.250.0 0.0.0.63 10.0.0.0 0.255.255.255
 deny ip 192.168.250.0 0.0.0.63 172.16.0.0 0.15.255.255
 deny ip 192.168.250.0 0.0.0.63 1.1.1.0 0.0.0.255
 deny ip 192.168.250.0 0.0.0.63 2.2.2.0 0.0.0.255
 deny ip 192.168.250.0 0.0.0.63 203.0.113.0 0.0.0.255
 remark internet
 permit ip 192.168.250.0 0.0.0.63 any
!
interface vlan 250
 ip access-group CEBU-SALES-IN in
```

---

## Test matrix

Run each test and keep the screenshot under `docs/images/`. Use `show access-lists <name>` afterward: the match counter on the line that handled the packet is the evidence.

| From | Test | Expected |
|---|---|---|
| Any user VLAN PC | Release and renew DHCP | Works |
| Any user VLAN PC | Ping 8.8.8.8 | Works |
| Sales PC | Ping the server (192.168.50.4) | Works |
| Sales PC | Ping an IT PC | Fails |
| IT PC | Ping a Sales PC | Works (the `echo-reply` line's counter increases) |
| HR or Finance PC | Ping any VLAN except Server | Fails |
| Engineering PC | Ping an Operations PC | Works |
| Engineering PC | Ping a Sales PC | Fails |
| Customer Support PC | Ping a Sales PC | Works |
| Management PC | Ping an HR PC | Works |
| Management PC | Ping an IT PC | Fails |
| Guest device | Ping 8.8.8.8 | Works |
| Guest device | Ping any internal address | Fails |
| IT PC | Ping a guest device | Works |
| HQ phone | Call a CEBU phone | Works |
| Any phone | Ping 8.8.8.8 | Fails |
| CEBU Sales PC | Ping the HQ server | Works |
| CEBU Management PC | Ping an HQ Management PC | Works |
