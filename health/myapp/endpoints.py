import json

from django.http import QueryDict, JsonResponse
from django.views.decorators.csrf import csrf_exempt


def get_request_data(request):
	"""
	Retrieves the request data irrespective of the method and type it was send.
	@param request: The Django HttpRequest.
	@type request: WSGIRequest
	@return: The data from the request as a dict
	@rtype: QueryDict
	"""
	try:
		data = None
		if request is not None:
			request_meta = getattr(request, 'META', {})
			request_method = getattr(request, 'method', None)
			if request_meta.get('CONTENT_TYPE', '') == 'application/json':
				data = json.loads(request.body)
			elif str(request_meta.get('CONTENT_TYPE', '')).startswith('multipart/form-data;'):  # Special handling for
				# Form Data?
				data = request.POST.copy()
				data = data.dict()
			elif request_method == 'GET':
				data = request.GET.copy()
				data = data.dict()
			elif request_method == 'POST':
				data = request.POST.copy()
				data = data.dict()
			if not data:
				request_body = getattr(request, 'body', None)
				if request_body:
					data = json.loads(request_body)
				else:
					data = QueryDict()
			return data
	except Exception as e:
		print.exception('get_request_data Exception: %s', e)
	return QueryDict()
class googleManager(object):
	@csrf_exempt
	@staticmethod
	def google_calender(request):
		try:
			data = get_request_data(request)
			print(data)
			return JsonResponse()
		except Exception as rehema:
			print('upload exception: %s' % rehema)
		return JsonResponse({'code': '600.003.001', 'message': 'general fail'})