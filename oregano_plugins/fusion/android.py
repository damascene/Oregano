from oregano.plugins import hook

from .plugin import FusionPlugin
from .conf import Conf


class Plugin(FusionPlugin):

    @hook
    def on_new_window(self, window):
        if window.wallet and Conf(wallet=window.wallet).autofuse:
            self.add_wallet(window.wallet, password=window.wallet_password)
            self.enable_autofusing(window.wallet, password=window.wallet_password)
        # window.wallet_password = None

    #@hook
    def spendable_coin_filter(self, wallet, coins):
        """ Invoked by the send tab to filter out coins that aren't fused if the wallet has
        'spend only fused coins' enabled. """
        if not coins:
            return

        if not Conf(wallet).spend_only_fused_coins or not self.wallet_can_fuse(wallet):
            return

        # external_coins_addresses is only ever used if they are doing a sweep. in which case we always allow the coins
        # involved in the sweep
        # external_coin_addresses = set()
        # if hasattr(window, 'tx_external_keypairs'):
        #     for pubkey in window.tx_external_keypairs:
        #         a = Address.from_pubkey(pubkey)
        #         external_coin_addresses.add(a)

        # we can ONLY spend fused coins + ununfused living on a fused coin address
        fuz_adrs_seen = set()
        fuz_coins_seen = set()
        with wallet.lock:
            for coin in coins.copy():
                # if coin['address'] in external_coin_addresses:
                #     # completely bypass this filter for external keypair dict
                #     # which is only used for sweep dialog in send tab
                #     continue
                fuse_depth = Conf(wallet).fuse_depth
                is_fuz_adr = self.is_fuz_address(wallet, coin['address'], require_depth=fuse_depth-1)
                if is_fuz_adr:
                    fuz_adrs_seen.add(coin['address'])
                # we allow coins sitting on a fused address to be "spent as fused"
                if not self.is_fuz_coin(wallet, coin, require_depth=fuse_depth-1) and not is_fuz_adr:
                    coins.remove(coin)
                else:
                    fuz_coins_seen.add(get_coin_name(coin))
            # Force co-spending of other coins sitting on a fuzed address
            for adr in fuz_adrs_seen:
                adr_coins = wallet.get_addr_utxo(adr)
                for name, adr_coin in adr_coins.items():
                    if (name not in fuz_coins_seen
                            and not adr_coin['is_frozen_coin']
                            and adr_coin.get('slp_token') is None
                            and not adr_coin.get('token_data')
                            and not adr_coin.get('coinbase')):
                        coins.append(adr_coin)
                        fuz_coins_seen.add(name)

    def get_wallet_conf(self, wallet):
        return Conf(wallet)

    def set_fusion_mode(self, wallet, mode):
        assert mode in ['normal', 'fan-out', 'consolidate']
        Conf(wallet).fusion_mode = mode
