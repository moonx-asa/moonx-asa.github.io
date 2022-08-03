
function byteArrayToBase64(buffer) {
    let binary = '';
    let bytes = new Uint8Array(buffer);
    let len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

const WALLET_CHOICES = ['myalgo', 'algosigner', 'pera'];

class WalletWrapper {

    constructor(wallet_choice=null, ledger='TestNet') {
        this.wallet_choice = wallet_choice;
        this.ledger = ledger;
        this.accounts = [];
        this.address = null;
        this.connected = false;
        this.on_connect_callback = async() => {};
        this.on_disconnect_callback = async() => {};

        if (this.wallet_choice == 'myalgo') {
            this.connector = new window.MyAlgoConnect();

        } else if (this.wallet_choice == 'pera') {
            this.connector = new window.WalletConnect({
                bridge: "https://bridge.walletconnect.org",
                qrcodeModal: window.QRCodeModal,
            });

            // Initialize WalletConnect
            this.connector.on("disconnect", (error, payload) => {
                if (error) { throw error; }
                window.location.href = "/disconnect";
                return;
            });
            
            $('#auth_disconnect').click((e)=>{
                this.connector.killSession();
                return true;
            });

        } else if (this.wallet_choice == 'algosigner') {
            this.connector = window.AlgoSigner;
        }
    }

    // wrapper Methods
    connect = async(on_connect_callback) => {

        // connect with myalgo
        if (this.wallet_choice == 'myalgo') {
            this.accounts = await this.connect_myalgo();
            await on_connect_callback(this.accounts);

        // connect with algosigner
        } else if (this.wallet_choice == 'algosigner') {
            this.accounts = await this.connect_algosigner();
            await on_connect_callback(this.accounts);

        // connect with walletconnect
        } else if (this.wallet_choice == 'pera') {
            await this.connect_pera(on_connect_callback);
        }

        this.connected = true;
        if (this.accounts.length == 1) {
            this.set_address(this.accounts[0]);
        }
    }

    connect_myalgo = async() => {
        let got_accounts = await this.connector.connect();
        let accounts_array = [];
        for (let i in got_accounts) {
            accounts_array.push(got_accounts[i].address);
        }
        return accounts_array;
    }

    connect_algosigner = async() => {
        await this.connector.connect();
        let got_accounts = await this.connector.accounts({ ledger: this.ledger });
        let accounts_array = []
        for (let i in got_accounts) {
            accounts_array.push(got_accounts[i].address);
        }
        return accounts_array;
    }

    connect_pera = async(on_connect_callback) => {
        // Check if connection is already established
        if (this.connector.connected) {
            await this.connector.killSession();
        }
        
        this.connector.createSession();
        await (new Promise(resolve => {
            this.connector.on("connect", async(error, payload) => {
                if (error) { throw error; }
                this.accounts = payload.params[0]['accounts'];
                setTimeout(async() => {
                    await on_connect_callback(this.accounts);
                }, 4000); // XXX: Temp workaround, delay 4 seconds
                resolve();
            });
        }));
        return this.accounts;
    }

    sign = async(txns) => {
        // sign with myalgo
        if (this.wallet_choice == 'myalgo') {
            return await this.sign_myalgo(txns);

        // sign with algosigner
        } else if (this.wallet_choice == 'algosigner') {
            return await this.sign_algosigner(txns);

        // connect with walletconnect
        } else if (this.wallet_choice == 'pera') {
            return await this.sign_pera(txns);
        }
    }

    sign_myalgo = async(txns) => {
        let prepped_txns = [];
        for (let i in txns) {
            if ('signers' in txns[i]) {
                if (txns[i].signers.length == 0) { continue; }
            }
            prepped_txns.push(txns[i].txn);
        }
        return await this.connector.signTransaction(prepped_txns);
    }

    sign_algosigner = async(txns) => {
        return await this.connector.signTxn(txns);
    }

    sign_pera = async(txns) => {
        // Sign transaction
        const requestParams = [txns];

        const request = formatJsonRpcRequest("algo_signTxn", requestParams);
        //let result = this.connector.sendCustomRequest(request);
        const result = await this.connector.sendCustomRequest(request);
        return result;

        /*
        const decodedResult = result.map(element => {
            let element = new Blob(Buffer.from(element, "base64"))
        });
        return decodedResult;
        */
    }

    get_blob = (signed_txn) => {
        if (this.wallet_choice == 'myalgo') {
            let buffer = [];
            for (let k in signed_txn['blob']) {
                buffer.push(signed_txn['blob'][k]);
            }
            return btoa(String.fromCharCode.apply(null, buffer));
        } else if (this.wallet_choice == 'algosigner') {
            return signed_txn.blob;
        } else if (this.wallet_choice == 'pera') {
            return byteArrayToBase64(signed_txn);
        }
    }

    // helper methods
    set_address = (address) => {
        if (!this.accounts.includes(address)) {
            throw new Error('Address not in accounts.');
        }
        this.address = address;
    }
}

