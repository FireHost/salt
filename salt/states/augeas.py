import logging

logger = logging.getLogger(__name__)


def setvalue(value):
    ret = {'setvalue': value,
           'result': True,
           'comment': ''}

    if __opts__['test']:
        ret['comment'] = 'No changes made for testing'
        return ret

    result = __salt__['augeas.setvalue'](value)

    if not ['retval']:
        ret['result'] = False
        ret['comment'] = result['error']
    return ret


def remove(path):
    ret = {'remove': path,
           'result': True,
           'comment': ''}

    if __opts__['test']:
        ret['comment'] = 'No changes made for testing'
        return ret

    result = __salt__['augeas.remove'](path)

    if not ['retval']:
        ret['result'] = False
        ret['comment'] = result['error']
        return ret

    ret['comment'] = 'Changed %i lines' % result['count']
    return ret
