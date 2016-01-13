# -*- coding: utf-8 -*-
import os
import time
from bottle import route, run, template, post, request, response
import urllib
import urllib2
import json, simplejson

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

@route('/evaluation', method=['OPTIONS', 'POST'])
@enable_cors
def evaluate() :
	correct = 0

	data = request.body.read()
	print data
	# load questions & language
	input_json = json.loads(data)
	lang = input_json['language']

	conf = {}
	try :
		conf['kb'] = input_json['conf']['kb']
	except :
		print 'using default kb'
	try :
		conf['dm'] = input_json['conf']['dm']
	except :
		print 'using default dm'
	try :
		conf['tgm'] = input_json['conf']['tgm']
	except :
		print 'using default tgm'
	try :
		conf['qgm'] = input_json['conf']['qgm']
	except :
		print 'using default qgm'
	try :
		conf['answer_num'] = input_json['conf']['answer_num']
	except :
		print 'using default qgm'

	f = open('nlq1_vis.json')
	data = f.read().replace('\xef\xbb\xbf','')
	questions = json.loads(data)
	f.close()
	
	for question in questions : 
		if lang == question['lang'] : 
			data = {}
			data['language'] = lang
			data['string'] = question['question']
			data['conf'] = conf
			print question['question']
			result = send_postrequest("http://121.254.173.77:7040/controller", json.dumps(data))
			answers = []
			for answer in json.loads(result)['answers'].split('\n')[:-1] : 
				pos = answer.rfind('//')
				answer = answer[pos+1:].replace('_', ' ').lower()
				answers.append(answer)

			print answers
			if question['answer'].lower() in answers : 
				correct += 1 

	
	print "correct : " + str(correct)
	return {'accuracy':float(correct)/len(questions)}
	
#	print input_json
#	doc_type = input_json['type']

def send_postrequest(url, input_string):

	req = urllib2.Request(url, data=input_string.encode('utf-8'), headers={'Content-Type':'application/x-www-form-urlencoded; charset=utf-8'})
	f = urllib2.urlopen(req)
	data = f.read()

	f.close()
	return data.replace('\xef\xbb\xbf','')

run(server='cherrypy', host='121.254.173.77', port=31999, debug=True)
#run(host='121.254.173.77', port=31999, debug=True)
