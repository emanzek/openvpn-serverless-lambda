#!/bin/bash

# Source: https://git.io/vpn/openvpn-install.sh
# This script has been modified for my own use

os="ubuntu"
os_version=$(grep 'VERSION_ID' /etc/os-release | cut -d '"' -f 2 | tr -d '.')
group_name="nogroup"

# Acquiring IPv4 address
ip=$(ip -4 addr | grep inet | grep -vE '127(\.[0-9]{1,3}){3}' | cut -d '/' -f 1 | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}')

# Get public IP and sanitize with grep
public_ip=$(grep -m 1 -oE '^[0-9]{1,3}(\.[0-9]{1,3}){3}$' <<< "$(wget -T 10 -t 1 -4qO- "http://ip1.dynupdate.no-ip.com/" || curl -m 10 -4Ls "http://ip1.dynupdate.no-ip.com/")")
protocol=udp
port="1194"
client="$(date +%Y%m%dT%H%MZ)-client"
firewall="iptables"

echo "OpenVPN installation is ready to begin."
# Install a firewall if firewalld or iptables are not already available
if ! systemctl is-active --quiet firewalld.service && ! hash iptables 2>/dev/null; then
	if [[ "$os" == "centos" || "$os" == "fedora" ]]; then
		firewall="firewalld"
		# We don't want to silently enable firewalld, so we give a subtle warning
		# If the user continues, firewalld will be installed and enabled during setup
		echo "firewalld, which is required to manage routing tables, will also be installed."
	elif [[ "$os" == "debian" || "$os" == "ubuntu" ]]; then
		# iptables is way less invasive than firewalld so no warning is given
		firewall="iptables"
	fi
fi
# If running inside a container, disable LimitNPROC to prevent conflicts
if systemd-detect-virt -cq; then
	mkdir /etc/systemd/system/openvpn-server@server.service.d/ 2>/dev/null
	echo "[Service]
LimitNPROC=infinity" > /etc/systemd/system/openvpn-server@server.service.d/disable-limitnproc.conf
fi
	
# Install required package
apt-get update
apt-get install -y --no-install-recommends openvpn openssl ca-certificates $firewall

# Get easy-rsa
easy_rsa_url='https://github.com/OpenVPN/easy-rsa/releases/download/v3.2.0/EasyRSA-3.2.0.tgz'
mkdir -p /etc/openvpn/server/easy-rsa/
{ wget -qO- "$easy_rsa_url" 2>/dev/null || curl -sL "$easy_rsa_url" ; } | tar xz -C /etc/openvpn/server/easy-rsa/ --strip-components 1
chown -R root:root /etc/openvpn/server/easy-rsa/
cd /etc/openvpn/server/easy-rsa/
# Create the PKI, set up the CA and the server and client certificates
./easyrsa --batch init-pki
./easyrsa --batch build-ca nopass
./easyrsa --batch --days=3650 build-server-full server nopass
./easyrsa --batch --days=3650 build-client-full "$client" nopass
./easyrsa --batch --days=3650 gen-crl
# Move the stuff we need
cp pki/ca.crt pki/private/ca.key pki/issued/server.crt pki/private/server.key pki/crl.pem /etc/openvpn/server
# CRL is read with each client connection, while OpenVPN is dropped to nobody
chown nobody:"$group_name" /etc/openvpn/server/crl.pem
# Without +x in the directory, OpenVPN can't run a stat() on the CRL file
chmod o+x /etc/openvpn/server/
# Generate key for tls-crypt
openvpn --genkey secret /etc/openvpn/server/tc.key
# Create the DH parameters file using the predefined ffdhe2048 group
echo '-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA//////////+t+FRYortKmq/cViAnPTzx2LnFg84tNpWp4TZBFGQz
+8yTnc4kmz75fS/jY2MMddj2gbICrsRhetPfHtXV/WVhJDP1H18GbtCFY2VVPe0a
87VXE15/V8k1mE8McODmi3fipona8+/och3xWKE2rec1MKzKT0g6eXq8CrGCsyT7
YdEIqUuyyOP7uWrat2DX9GgdT0Kj3jlN9K5W7edjcrsZCwenyO4KbXCeAvzhzffi
7MA0BM0oNC9hkXL+nOmFg/+OTxIy7vKBg8P+OxtMb61zO7X8vC7CIAXFjvGDfRaD
ssbzSibBsu/6iGtCOGEoXJf//////////wIBAg==
-----END DH PARAMETERS-----' > /etc/openvpn/server/dh.pem
# Generate server.conf
echo "local $ip
port $port
proto $protocol
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
auth SHA512
tls-crypt tc.key
topology subnet
server 10.8.0.0 255.255.255.0" > /etc/openvpn/server/server.conf
	
# IPv6
echo 'push "redirect-gateway def1 bypass-dhcp"' >> /etc/openvpn/server/server.conf
echo 'ifconfig-pool-persist ipp.txt' >> /etc/openvpn/server/server.conf

# DNS
# Locate the proper resolv.conf
# Needed for systems running systemd-resolved
if grep '^nameserver' "/etc/resolv.conf" | grep -qv '127.0.0.53' ; then
	resolv_conf="/etc/resolv.conf"
else
	resolv_conf="/run/systemd/resolve/resolv.conf"
fi
# Obtain the resolvers from resolv.conf and use them for OpenVPN
grep -v '^#\|^;' "$resolv_conf" | grep '^nameserver' | grep -v '127.0.0.53' | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}' | while read line; do
	echo "push \"dhcp-option DNS $line\"" >> /etc/openvpn/server/server.conf
done
	
echo 'push "block-outside-dns"' >> /etc/openvpn/server/server.conf
echo "keepalive 10 120
user nobody
group $group_name
persist-key
persist-tun
verb 3
crl-verify crl.pem" >> /etc/openvpn/server/server.conf

echo "explicit-exit-notify" >> /etc/openvpn/server/server.conf
# Enable net.ipv4.ip_forward for the system
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-openvpn-forward.conf
# Enable without waiting for a reboot or service restart
echo 1 > /proc/sys/net/ipv4/ip_forward
	
# Create a service to set up persistent iptables rules
iptables_path=$(command -v iptables)
# nf_tables is not available as standard in OVZ kernels. So use iptables-legacy
# if we are in OVZ, with a nf_tables backend and iptables-legacy is available.
if [[ $(systemd-detect-virt) == "openvz" ]] && readlink -f "$(command -v iptables)" | grep -q "nft" && hash iptables-legacy 2>/dev/null; then
	iptables_path=$(command -v iptables-legacy)
fi
echo "[Unit]
Before=network.target
[Service]
Type=oneshot
ExecStart=$iptables_path -t nat -A POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $ip
ExecStart=$iptables_path -I INPUT -p $protocol --dport $port -j ACCEPT
ExecStart=$iptables_path -I FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStart=$iptables_path -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
ExecStop=$iptables_path -t nat -D POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $ip
ExecStop=$iptables_path -D INPUT -p $protocol --dport $port -j ACCEPT
ExecStop=$iptables_path -D FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStop=$iptables_path -D FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT" > /etc/systemd/system/openvpn-iptables.service
echo "RemainAfterExit=yes
[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/openvpn-iptables.service
systemctl enable --now openvpn-iptables.service

# If the server is behind NAT, use the correct IP address
[[ -n "$public_ip" ]] && ip="$public_ip"

# client-common.txt is created so we have a template to add further users later
echo "client
dev tun
proto $protocol
remote $ip $port
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
ignore-unknown-option block-outside-dns
verb 3" > /etc/openvpn/server/client-common.txt
# Enable and start the OpenVPN service
systemctl enable --now openvpn-server@server.service

# Generates the custom client.ovpn
cat /etc/openvpn/server/client-common.txt > ~/"$client".ovpn
echo "<ca>" >> ~/"$client".ovpn
cat /etc/openvpn/server/easy-rsa/pki/ca.crt >> ~/"$client".ovpn
echo "</ca>" >> ~/"$client".ovpn
echo "<cert>" >> ~/"$client".ovpn
sed -ne '/BEGIN CERTIFICATE/,$ p' /etc/openvpn/server/easy-rsa/pki/issued/"$client".crt >> ~/"$client".ovpn
echo "</cert>" >> ~/"$client".ovpn
echo "<key>" >> ~/"$client".ovpn
cat /etc/openvpn/server/easy-rsa/pki/private/"$client".key >> ~/"$client".ovpn
echo "</key>" >> ~/"$client".ovpn
echo "<tls-crypt>" >> ~/"$client".ovpn
sed -ne '/BEGIN OpenVPN Static key/,$ p' /etc/openvpn/server/tc.key >> ~/"$client".ovpn
echo "</tls-crypt>" >> ~/"$client".ovpn

echo "Finished!"
echo "The client configuration is available in:" ~/"$client.ovpn"

echo "Upload client configuration to S3"

# Upload ovpn file to S3
aws s3 cp ~/"$client".ovpn s3://openvpn-bot-storage/client/
