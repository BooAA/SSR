import os

class ssr_monitor:

    ssr_path = ""

    def __init__(self, path = '/sys/kernel/rdma_rxe') -> None:
        self.ssr_path = path

    def get_qp_list(self) -> list:
        return os.listdir(self.ssr_path)

    def get_qp_counters(self, qpn) -> dict:
        qp_dir_path = os.path.join(self.ssr_path, str(qpn))
        ret = {}
        
        try:
            for counter in os.listdir(qp_dir_path):
                with open(os.path.join(qp_dir_path, counter)) as file:
                    for line in file:
                        ret[counter] = int(line)
        except:
            pass

        return ret