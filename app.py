import flask
from ipaddress import ip_address, ip_network
from fileinput import filename
import pandas as pd
app = flask.Flask(__name__)
  
@app.route('/')  
def main():  
    return flask.render_template("Index.html")  
  
@app.route('/dumproutinginfo', methods = ['POST'])  
def dumproutinginfo():  
    if flask.request.method == 'POST':  
        f = flask.request.files['file']
        f.save(f.filename)
        ip = flask.request.form['ip']
        result = range_search(ip, f.filename, False) 
        return flask.render_template("dumproutingOutput.html", privateprimary=result[0],privatesecondary=result[1],microsoftprimary=result[2],microsoftsecondary=result[3],publicprimary=result[4],publicsecondary=result[5])
    else:
        return('Something went wrong, please retry')

@app.route('/effectiveroutes', methods = ['POST'])  
def effectiveroutes():  
    if flask.request.method == 'POST':  
        f = flask.request.files['file']
        filename = f.filename
        try:
            extension = filename.split('.')[1]
            if extension != 'csv':
               read_file = pd.read_excel(f.filename)
               filename = filename.split('.')[0] + '.csv'
               read_file.to_csv(filename, index=None,header=True)
        except:
            return('Invalid file')
        f.save(f.filename)
        ip = flask.request.form['ip']
        result = range_search(ip, f.filename, True) 
        result = result.split(',')
        return flask.render_template("effectiveroutesOutput.html", routesource=result[0], destinationsubnets=result[1],destinationservicetags=result[2],nexthoptype=result[3],nexthops=result[4],isenabled=result[5])
    else:
        return('Something went wrong, please retry') 

def range_search(ip, filename, effectiveroutes):
    try:
        addr = ip_address(ip)
    except:
        # add file delete
        return('The submitted IP is not in the correct format.')
    output = ''
    if effectiveroutes:
        output = effectiveroutes_parser(filename, addr)
    else:
        f = open(filename, 'r')
        lines = f.readlines()
        if '-cis-' in lines[2]:
            output = dumprouting_cisco_parser(filename, addr)
        else:
            output = dumprouting_juniper_parser(filename, addr)
    # add file delete
    return output

def effectiveroutes_parser(filename, ip):
    file = open(filename, 'r')
    lines = file.readlines()
    output = ''
    if effectiveroutes:
        bestPrefix = 0
        for line in lines:
            aux = line.split(',')
            for range in aux:
                if '/' in range and range != 'N/A':
                    if '"' in range:
                        aux2 = range.split(',')
                        for aux3 in aux2:
                            if '"' in aux3:
                                aux3 = aux3.split('"')
                                for aux4 in aux3:
                                    if "/" in aux4:
                                        net = aux4
                                        break
                                net = ip_network(net.split()[0], strict=False)
                                if ip in net:
                                    if net.prefixlen >= bestPrefix:
                                        bestPrefix = net.prefixlen
                                        output = line
                            else:
                                continue
                    else:
                        net = ip_network(range.split()[0], strict=False)
                        if ip in net:
                            if net.prefixlen >= bestPrefix:
                                bestPrefix = net.prefixlen
                                output = line
                else:
                    continue
    file.close()
    return output

def dumprouting_cisco_parser(filename, ip):
    file = open(filename, 'r')
    lines = file.readlines()
    privatePrimaryOutput = ''
    privateSecondaryOutput = ''
    msPrimaryOutput = ''
    msSecondaryOutput = ''
    publicPrimaryOutput = ''
    publicSecondaryOutput = ''
    output = [privatePrimaryOutput, privateSecondaryOutput, msPrimaryOutput, msSecondaryOutput, publicPrimaryOutput, publicSecondaryOutput]
    wordMap = {'Private':0,'Microsoft':2,'Public':4}
    position = 0
    for line in lines:
        if 'DeviceName:' in line:
            aux = line.split(', ')
            deviceName = aux[4].split(':')[1]
            peeringType = aux[3].split(':')[1]
            position  = wordMap[peeringType]
            wordMap[peeringType] += 1
            bestPrefix = 0
            continue
        aux = line.split()
        if len(aux)>0:
            if aux[0] == 'B' or aux[0] == 'L' or aux[0] == 'C':
                try:
                    net = ip_network(aux[1], strict=False)
                except:
                    continue
                if ip in net and net.prefixlen >= bestPrefix:
                    bestPrefix = net.prefixlen
                    output[position] = line
    file.close()
    return output

def dumprouting_juniper_parser(filename, ip):
    file = open(filename, 'r')
    lines = file.readlines()
    privatePrimaryOutput = ''
    privateSecondaryOutput = ''
    msPrimaryOutput = ''
    msSecondaryOutput = ''
    publicPrimaryOutput = ''
    publicSecondaryOutput = ''
    output = [privatePrimaryOutput, privateSecondaryOutput, msPrimaryOutput, msSecondaryOutput, publicPrimaryOutput, publicSecondaryOutput]
    wordMap = {'Private':0,'Microsoft':2,'Public':4}
    position = 0
    for i in range(0,len(lines)):
        if 'DeviceName:' in lines[i]:
            aux = lines[i].split(', ')
            deviceName = aux[4].split(':')[1]
            peeringType = aux[3].split(':')[1]
            position  = wordMap[peeringType]
            wordMap[peeringType] += 1
            bestPrefix = 0
            continue
        aux = lines[i].split()
        if len(aux) > 0:
            if '.' in aux[0] and '/' in aux[0]:
                try:
                    net = ip_network(aux[0], strict=False)
                except:
                    continue
                if ip in net and net.prefixlen >= bestPrefix:
                    output[position] = lines[i]
                    while True:
                        i += 1
                        if(('.' in lines[i] and '/' in lines[i]) or 'ii. GetBgpPeering Info' in lines[i]):
                            i -= 1
                            break
                        output[position] += lines[i]
    file.close()
    return output


