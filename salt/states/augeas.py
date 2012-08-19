import logging

logger = logging.getLogger(__name__)


def setvalue(name):
    ret = {'setvalue': name,
           'result': True,
           'changes': {},
           'comment': ''}

    if __opts__['test']:
        ret['comment'] = 'No changes made for testing'
        return ret

    result = __salt__['augeas.setvalue'](name)

    if not ['retval']:
        ret['result'] = False
        ret['comment'] = result['error']
    return ret


def remove(name):
    ret = {'remove': name,
           'result': True,
           'changes': {},
           'comment': ''}

    if __opts__['test']:
        ret['comment'] = 'No changes made for testing'
        return ret

    result = __salt__['augeas.remove'](name)

    if not ['retval']:
        ret['result'] = False
        ret['comment'] = result['error']
        return ret

    ret['comment'] = 'Changed %i lines' % result['count']
    if result['count'] > 0:
        ret['changes'] = {'removed': result['count']}
    return ret
