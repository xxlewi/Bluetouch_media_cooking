
import sys
from router import Router

ip_router = "192.168.88.1"



if len(sys.argv) > 1:
    operator = sys.argv[1]
else:
    operator = None

router = Router(ip_router, operator)


# router.connecting()




router.update_firmware()
# router.create_and_add_vpn()

# router.check_name()




    