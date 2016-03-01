from flask import Blueprint, request, jsonify
from requests.exceptions import HTTPError, Timeout, RequestException

from alg import download_image
from utils import make_hash
from validation import ImageInputs, ValidationError


views = Blueprint('views', __name__)


@views.errorhandler(ValidationError)
def handle_invalid_usage(error):
    response = jsonify(success=False, errors=error.errors)
    response.status_code = error.status_code
    return response


def format_image(image_data):
    return image_data


@views.route('/', defaults={'image_url': ''})
@views.route('/<path:image_url>')
def image(image_url=''):

    # TODO strip args from image_url
    # Subclass werkzeug.routing.PathConverter to only match on pre-query params (?.*)

    params = {
        'url': image_url,
    }
    # print params
    # print request.args
    # print request.view_args

    params_hash = make_hash(params)
    # print params_hash

    # Have we already processed this image?
    # existing_image_data = app.redis.get(params_hash)
    # if existing_image_data:
    #     return format_image(existing_image_data)

    # Validate
    inputs = ImageInputs(request)
    if not inputs.validate():
        response = jsonify(success=False, errors=inputs.errors)
        response.status_code = 400
        return response

    # Now download image and check type
    try:
        image = download_image(image_url)

    except HTTPError as e:
        # Non-2xx status code
        errors = ['URL returned a {} status code'.format(e.response.status_code)]
        raise ValidationError(errors)

    except Timeout as e:
        errors = ['URL timed out']
        raise ValidationError(errors)

    except RequestException as e:
        # TODO log other errors
        print 'misc error'
        print image_url, e
        errors = ['URL is not a valid image']
        raise ValidationError(errors)

    except Exception:
        # TOOD catch these
        raise

    if image is None:
        errors = ['URL is not a valid image']
        raise ValidationError(errors)

    print 'dimensions', image.shape

    # Set defaults to missing params
    params['args'] = request.args



    return jsonify(success=True, params=params)
    # request.args.get('', '')

    # Process

    # Cache results
    # app.redis.set(params_hash, params)

# TODO catch 20s timeout, complete job on worker?