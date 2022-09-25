import hashlib,requests,json,time,sys,os

user_private_key=""

def send_block(block):
    res=requests.post("https://halcoin.halwarsing.net/HalCoiN?type=addBlock&private_key="+user_private_key,data={'block':json.dumps(block)})
    return res.json()

def get_last_block():
    res=requests.get("https://halcoin.halwarsing.net/HalCoiN?type=getLastBlock&private_key="+user_private_key)
    return res.json()

def get_transactions():
    res=requests.get("https://halcoin.halwarsing.net/HalCoiN?type=getNotAllowedTransactions&private_key="+user_private_key)
    return res.json()

def mine_hash(prev_hash,conv_hash,prev_mrkl_root,max_nonce=100000):
    for nonce in range(max_nonce):
        hash=hashlib.sha256((prev_hash+conv_hash+prev_mrkl_root+str(nonce)).encode('utf8')).hexdigest()
        if hash.startswith('0'):
            return (hash,nonce)
    return 0

def mine_block(result,prev_hash,prev_mrkl_root,max_nonce=100000,max_mine_nonce=100):
    for i in range(max_mine_nonce):
        conv_hash=hashlib.sha256(("HalCoiNMiner v0.0.1 #"+str(i)).encode('utf8')).hexdigest()
        start_time=time.time()
        res=mine_hash(prev_hash,conv_hash,prev_mrkl_root,max_nonce)
        end_time=time.time()
        if res!=0:
            res_json=send_block({
                "hash":res[0],
                "prev_hash":prev_hash,
                "conv_hash":conv_hash,
                "prev_mrkl_root":prev_mrkl_root,
                "nonce":res[1],
                "trs":get_transactions()
            })

            if res_json['code']==0:
                result['hash']=res[0]
                result['prev_hash']=prev_hash
                result['conv_hash']=conv_hash
                result['prev_mrkl_root']=prev_mrkl_root
                result['nonce']=res[1]
                result['time']=end_time-start_time
                result['speed']=res[1] if result['time']<=1.0 else res[1]/result['time']
                return 0
            if res_json['code']==5:
                continue
            elif res_json['code']==2:
                return 2
            elif res_json['code']==10:
                return 3
            elif res_json['code']==15:
                return 4
            elif res_json['code']==16:
                return 5
            elif res_json['code']==17:
                return 6
            elif res_json['code']==18:
                return 7
            elif res_json['code']==19:
                return 8
    return 1

def mine(result,max_nonce=100000,max_mine_nonce=100,sleep_time=600):
    lastBlock=get_last_block()
    res=mine_block(result,lastBlock['hash'],lastBlock['mrkl_root'])
    if res==1:
        time.sleep(sleep_time)
    elif res==2:
        run=False
        return 2
    elif res>=3 and res<=8:return res
    return 0

def run_mine(max_nonce=100000,max_mine_nonce=100,sleep_time=600):
    try:
        while True:
            result={}
            err=mine(result,max_nonce,max_mine_nonce=100,sleep_time=600)
            if err==0:
                print('Block Mined')
                print('HASH          : '+result['hash'])
                print('PREV_HASH     : '+result['prev_hash'])
                print('CONV_HASH     : '+result['conv_hash'])
                print('PREV_MRKL_ROOT: '+result['prev_mrkl_root'])
                print('NONCE         : '+str(result['nonce']))
                print('TIME          : '+str(result['time'])+' s')
                print('SPEED         : '+str(result['speed'])+' H/s')
                print('URL           : https://halcoin.halwarsing.net/block/'+result['hash'])
                print()
    except KeyboardInterrupt:
        print('exit')

if __name__=="__main__":
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    with open(os.path.join(application_path,"config.json"),"r") as file:
        config=json.loads(file.read())
        user_private_key=config['private_key']
        file.close()
        run_mine(config['max_nonce'],config['max_mine_nonce'],config['sleep_time'])
