#!/usr/bin/env python3
from camera import Camera
from flask import Flask, Response, render_template, jsonify
import sys

HOST = '0.0.0.0'
PORT = '8000'

class VisionApp:
		def __init__(self):
			self.camera = Camera()
			self.app = Flask(__name__)
			self.add_routes()

		def add_routes(self):
			self.app.add_url_rule('/', view_func=self.index)
			self.app.add_url_rule('/video_feed', view_func=self.video_feed)
			self.app.add_url_rule('/status', view_func=self.status)
			self.app.add_url_rule('/chomp', view_func=self.chomp)
			self.app.add_url_rule('/sources', view_func=self.sources)

		def run(self):
			self.app.run(host=HOST, port=PORT, use_reloader=False)

		def local_feed(self):
			self.camera.display_live_feed()

		####################  ROUTES  ####################
		
		def index(self):
			return render_template('index.html')

		def sources(self):
			return render_template('sources.html')

		def video_feed(self):
			return Response(self.camera.get_feed(), mimetype = 'multipart/x-mixed-replace; boundary=frame')

		def status(self):
			if self.camera.left_hand_raised() and self.camera.right_hand_raised():
					status_text = 'Both Hands Raised'
			elif self.camera.left_hand_raised() and not self.camera.right_hand_raised():
				status_text = 'Left Hand Raised'
			elif not self.camera.left_hand_raised() and self.camera.right_hand_raised():
				status_text = 'Right Hand Raised'
			else:
				status_text = 'No Hands Raised'

			return jsonify({'status': status_text})
		
		def chomp(self):
			if self.camera.chomping():
				status_text = 'Chomping'
			else:
				status_text = 'Not Chomping'

			return jsonify({'status': status_text})

		##################################################


if __name__ == '__main__':
	app = VisionApp()
	if len(sys.argv) > 1 and sys.argv[1] == 'local':
		print('Displaying feed locally')
		app.local_feed()
	else:
		app.run()