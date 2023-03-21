import flask
from ipaddress import ip_address, ip_network
from fileinput import filename
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
        return flask.render_template("Output.html", range=result)
    else:
        return('Something went wrong, please retry')

@app.route('/effectiveroutes', methods = ['POST'])  
def effectiveroutes():  
    if flask.request.method == 'POST':  
        f = flask.request.files['file']
        try:
            extension = f.filename.split('.')[1]
            if extension != 'csv':
                return('Uploaded file is not csv, please upload the effective route excel file in the csv format')
        except:
            return('Uploaded file is not csv, please upload the effective routes excel file in the csv format')
        f.save(f.filename)
        ip = flask.request.form['ip']
        result = range_search(ip, f.filename, True) 
        return flask.render_template("Output.html", range=result)
    else:
        return('Something went wrong, please retry') 

def range_search(ip, filename, effectiveroutes):
    try:
        addr = ip_address(ip)
    except:
        # add file delete
        return('The submitted IP is not in the correct format.')
    file = open(filename, 'r')
    lines = file.readlines()
    output = ''
    if effectiveroutes:
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
                                if addr in net:
                                    output += aux4 + '\n'
                            else:
                                next
                    else:
                        net = ip_network(range.split()[0], strict=False)
                        if addr in net:
                            output += range + '\n'
                else:
                    next
    else:
        for line in lines:
            aux = line.split()
            if len(aux) > 0:
                if aux[0] == 'B' or aux[0] == 'L' or aux[0] == 'C' or '/' in aux[0]:
                    if '/' not in aux[0]:
                        net = ip_network(aux[1], strict=False)
                    else:
                        net = ip_network(aux[0], strict=False)
                    if addr in net:
                        output += aux[1] + '\n'
                else:
                    next
    file.close()
    # add file delete
    return output