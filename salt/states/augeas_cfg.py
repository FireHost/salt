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


def setvalue(name, expressions):
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': 'No changes made'}

    from augeas import Augeas

    if len(expressions) < 1:
        ret['comment'] = "No expressions given"
        ret['result'] = False
        return ret

    if __opts__['test']:
        aug = Augeas(flags=Augeas.SAVE_NEWFILE)
        sfn = name
        dfn = '%s.augnew' % name
    else:
        aug = Augeas(flags=Augeas.SAVE_BACKUP)
        sfn = '%s.augsave' % name
        dfn = name

    if not os.path.isfile(name):
        ret['comment'] = "Unable to find file '%s'" % name
        ret['result'] = False
        return ret

    for (subpath, value) in expressions:
        try:
            aug.set('/files/%s/%s' % (name, subpath), value)
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

    # Augeas won't tell us if it made any changes, so we have to go about this
    # the hard way. The existence of the backup file will tell us.
    if os.path.isfile(sfn) and os.path.isfile(dfn):
        with nested(open(sfn, 'rb'), open(dfn, 'rb')) as (src, dst):
            diff = ''.join(difflib.unified_diff(src.readlines(),
                                                dst.readlines(),
                                                sfn,
                                                dfn))
        if __opts__['test']:
            if len(diff) > 0:
                ret['changes']['diff'] = diff
                ret['comment'] = ('Files differ, would make the following '
                                  'changes')
            os.remove(dfn)
        else:
            if len(diff) > 0:
                ret['changes']['diff'] = diff
                ret['comment'] = 'Changes made'
            os.remove(sfn)

    return ret


def remove(name):
    ret = {'name': name,
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
