import logging
import os
import difflib
from contextlib import nested

logger = logging.getLogger(__name__)


def __virtual__():
    try:
        from augeas import Augeas
        _ = Augeas
    except ImportError:
        return False
    else:
        return "augeas"


def setvalue(name, *expressions):
    ret = {'setvalue': name,
           'result': True,
           'changes': {},
           'comment': ''}

    import augeas

    if __opts__['test']:
        aug = augeas.Augeas(flags=augeas.SAVE_NEWFILE)
        sfn = name
        dfn = '%s.augnew' % name
    else:
        aug = augeas.Augeas(flags=augeas.SAVE_BACKUP)
        sfn = '%s.augsave' % name
        dfn = name

    if not os.path.isfile(name):
        ret['comment'] = "Unable to find file '%s'" % name
        ret['result'] = False
        return ret

    for expr in expressions:
        try:
            aug.set('/files/%s/%s' % (name, expr))
        except ValueError as e:
            ret['comment'] = 'Multiple values: %s' % e
            ret['result'] = False
            return ret

    try:
        aug.save()
    except IOError as e:
        ret['comment'] = str(e)
        ret['result'] = False
        return ret

    with nested(open(sfn, 'rb'), open(dfn, 'rb')) as (src, dst):
        diff = ''.join(difflib.unified_diff(sfn.readlines(),
                                            dfn.readlines(),
                                            sfn,
                                            dfn))
    if __opts__['test']:
        if len(diff) > 0:
            ret['comment'] = ('Files differ, would make the following '
                             'changes\n%s' % diff)
        os.remove(dfn)
    else:
        if len(diff) > 0:
            ret['changes']['diff'] = diff
            ret['comment'] = 'Changes made'
        os.remove(sfn)

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
