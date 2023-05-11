#!/bin/sh
# Como executar o script:
# chmod +x configura_gadget_usbcdc_daf.sh
# sudo ./configura_gadget_usbcdc_daf.sh
# Esse script tem como objetivo configurar um USB gadget
# da subclasse ACM no Raspberry Pi Zero.
# Além disso, vamos habilitar o funcionamento desse
# gadget no boot.
# referência: https://www.isticktoit.net/?p=1383
### Verifica se g_serial está contido no arquivo /boot/cmdline.txt
echo "Verificando módulo g_serial no /boot/cmdline.txt"
if grep --quiet g_serial /boot/cmdline.txt; then
    echo "Remova o módulo g_serial do arquivo /boot/cmdline.txt antes de proseguir."
    exit 1
else
    echo "Módulo g_serial não está presente, continuando."
fi
if ! grep --quiet modules-load=dwc2 /boot/cmdline.txt; then
    echo "modules-load=dwc2" >> /boot/cmdline.txt
fi
if ! grep --quiet dtoverlay=dwc2 /boot/config.txt; then
    echo "dtoverlay=dwc2"  >> /boot/config.txt
fi
if ! grep --quiet enable_uart=1 /boot/config.txt; then
    echo "enable_uart=1"  >> /boot/config.txt
fi
### Arquivo de configuração do USB Gadget ACM ###
ARQUIVO_CONFIG_GADGET=/usr/bin/gadget_daf.sh
echo "Criando arquivo ${ARQUIVO_CONFIG_GADGET}"
cat > ${ARQUIVO_CONFIG_GADGET} <<EOL
#!/bin/sh
mkdir -p "/sys/kernel/config/usb_gadget/DAF"
echo "0x0525" > "/sys/kernel/config/usb_gadget/DAF/idVendor"
echo "0xa4a7" > "/sys/kernel/config/usb_gadget/DAF/idProduct"
echo "0xEF" > "/sys/kernel/config/usb_gadget/DAF/bDeviceClass"
echo "0x02" > "/sys/kernel/config/usb_gadget/DAF/bDeviceSubClass"
echo "0x01" > "/sys/kernel/config/usb_gadget/DAF/bDeviceProtocol"
# STRINGS
mkdir -p "/sys/kernel/config/usb_gadget/DAF/strings/0x409"
echo "0123456789" > "/sys/kernel/config/usb_gadget/DAF/strings/0x409/serialnumber"
echo "DAF-SC" > "/sys/kernel/config/usb_gadget/DAF/strings/0x409/product"
echo "IFSC" > "/sys/kernel/config/usb_gadget/DAF/strings/0x409/manufacturer"
# CONFIGS
mkdir -p "/sys/kernel/config/usb_gadget/DAF/configs/c.1"
echo "0x80" > "/sys/kernel/config/usb_gadget/DAF/configs/c.1/bmAttributes"
echo "2" > "/sys/kernel/config/usb_gadget/DAF/configs/c.1/MaxPower"
mkdir -p "/sys/kernel/config/usb_gadget/DAF/configs/c.1/strings/0x409"
echo "CDC ACM" > "/sys/kernel/config/usb_gadget/DAF/configs/c.1/strings/0x409/configuration"
# FUNCTIONS
mkdir -p "/sys/kernel/config/usb_gadget/DAF/functions/acm.GS0"
ln -s "/sys/kernel/config/usb_gadget/DAF/functions/acm.GS0" "/sys/kernel/config/usb_gadget/DAF/configs/c.1"
# USB Device Controller (UDC)
basename /sys/class/udc/* > /sys/kernel/config/usb_gadget/DAF/UDC
EOL
chmod +x ${ARQUIVO_CONFIG_GADGET}
### Adiciona o arquivo de configuração acima para ser executado no boot
if grep --quiet ${ARQUIVO_CONFIG_GADGET} /etc/rc.local; then
    echo "Arquivo de configuração ${ARQUIVO_CONFIG_GADGET} já está contido no arquivo /etc/rc.local"
else
    echo "Adicionando o arquivo ${ARQUIVO_CONFIG_GADGET} em /etc/rc.local"
    # add o arquivo no /etc/rc.local antes do exit 0
    # para entender o seguinte comando sed
    # veja: https://stackoverflow.com/questions/1251999/how-can-i-replace-a-newline-n-using-sed
    # aqui usamos ',' ao invés de '/' para não interferir com o nome do arquivo que contém '/'.
    sed -i ':a;N;$!ba;s,\nexit,\n'"${ARQUIVO_CONFIG_GADGET}"'&,' /etc/rc.local
fi
### Adiciona módulos para iniciarem no boot
if grep --quiet dwc2 /etc/modules; then
    echo "Módulo dwc2 já está adicionado no arquivo /etc/modules."
else
    echo "Adicionando módulo dwc2 em /etc/modules"
    echo "dwc2" >> /etc/modules
fi
if grep --quiet libcomposite /etc/modules; then
    echo "Módulo libcomposite já está adicionado no arquivo /etc/modules."
else
    echo "Adicionando módulo libcomposite em /etc/modules"
    echo "libcomposite" >> /etc/modules
fi
echo "Pronto. Agora você precisa reiniciar o dispositivo para as configurações serem ativadas."