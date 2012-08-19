import logging

logger = logging.getLogger(__name__)


def setname(name):
    ret = {'setname': name,
           'result': True,
           'changes': {},
           'comment': ''}

    if __opts__['test']:
        ret['comment'] = 'No changes made for testing'
        return ret

    result = __salt__['augeas.setname'](name)

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
    ret['changes'] = {'removed': result['count']}
    return ret
