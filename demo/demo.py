"""
A demonstration workflow.
"""

from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow import specs, operators
from SpiffWorkflow.Workflow import Workflow, Task


def create_specs():
    wf = WorkflowSpec()
    # Build one branch.
    a1 = specs.Simple(wf, 'task_a1')
    wf.start.connect(a1)

    a2 = specs.Simple(wf, 'task_a2')
    a1.connect(a2)

    # Build another branch.
    b1 = specs.Simple(wf, 'task_b1')
    wf.start.connect(b1)

    b2 = specs.Simple(wf, 'task_b2')
    b1.connect(b2)

    # Merge both branches (synchronized).
    synch_1 = specs.Join(wf, 'synch_1')
    a2.connect(synch_1)
    b2.connect(synch_1)

    # If-condition that does not match.
    excl_choice_1 = specs.ExclusiveChoice(wf, 'excl_choice_1')
    synch_1.connect(excl_choice_1)

    c1 = specs.Simple(wf, 'task_c1')
    excl_choice_1.connect(c1)

    c2 = specs.Simple(wf, 'task_c2')
    cond = operators.Equal(
        operators.Attrib('test_attribute1'),
        operators.Attrib('test_attribute2'))
    excl_choice_1.connect_if(cond, c2)

    c3 = specs.Simple(wf, 'task_c3')
    excl_choice_1.connect_if(cond, c3)

    # If-condition that matches.
    excl_choice_2 = specs.ExclusiveChoice(wf, 'excl_choice_2')
    c1.connect(excl_choice_2)
    c2.connect(excl_choice_2)
    c3.connect(excl_choice_2)

    d1 = specs.Simple(wf, 'task_d1')
    excl_choice_2.connect(d1)

    d2 = specs.Simple(wf, 'task_d2')
    excl_choice_2.connect_if(cond, d2)

    d3 = specs.Simple(wf, 'task_d3')
    cond = operators.Equal(
        operators.Attrib('test_attribute1'),
        operators.Attrib('test_attribute1'))
    excl_choice_2.connect_if(cond, d3)

    # If-condition that does not match.
    multichoice = specs.MultiChoice(wf, 'multi_choice_1')
    d1.connect(multichoice)
    d2.connect(multichoice)
    d3.connect(multichoice)

    e1 = specs.Simple(wf, 'task_e1')
    multichoice.connect_if(cond, e1)

    e2 = specs.Simple(wf, 'task_e2')
    cond = operators.Equal(
        operators.Attrib('test_attribute1'),
        operators.Attrib('test_attribute2'))
    multichoice.connect_if(cond, e2)

    e3 = specs.Simple(wf, 'task_e3')
    cond = operators.Equal(
        operators.Attrib('test_attribute2'),
        operators.Attrib('test_attribute2'))
    multichoice.connect_if(cond, e3)

    # StructuredSynchronizingMerge
    syncmerge = specs.Join(wf, 'struct_synch_merge_1', 'multi_choice_1')
    e1.connect(syncmerge)
    e2.connect(syncmerge)
    e3.connect(syncmerge)

    # Implicit parallel split.
    f1 = specs.Simple(wf, 'task_f1')
    syncmerge.connect(f1)

    f2 = specs.Simple(wf, 'task_f2')
    syncmerge.connect(f2)

    f3 = specs.Simple(wf, 'task_f3')
    syncmerge.connect(f3)

    # Discriminator
    discrim_1 = specs.Join(wf,
                     'struct_discriminator_1',
                     'struct_synch_merge_1',
                     threshold=1)
    f1.connect(discrim_1)
    f2.connect(discrim_1)
    f3.connect(discrim_1)

    # Loop back to the first exclusive choice.
    excl_choice_3 = specs.ExclusiveChoice(wf, 'excl_choice_3')
    discrim_1.connect(excl_choice_3)
    cond = operators.NotEqual(
        operators.Attrib('excl_choice_3_reached'),
        operators.Attrib('two'))
    excl_choice_3.connect_if(cond, excl_choice_1)

    # Split into 3 branches, and implicitly split twice in addition.
    multi_instance_1 = specs.MultiInstance(wf, 'multi_instance_1', times=3)
    excl_choice_3.connect(multi_instance_1)

    # Parallel tasks.
    g1 = specs.Simple(wf, 'task_g1')
    g2 = specs.Simple(wf, 'task_g2')
    multi_instance_1.connect(g1)
    multi_instance_1.connect(g2)

    # StructuredSynchronizingMerge
    syncmerge2 = specs.Join(wf, 'struct_synch_merge_2', 'multi_instance_1')
    g1.connect(syncmerge2)
    g2.connect(syncmerge2)

    # Add a final task.
    last = specs.Simple(wf, 'last')
    syncmerge2.connect(last)

    # Add another final task :-).
    end = specs.Simple(wf, 'End')
    last.connect(end)

    return wf


if __name__ == '__main__':
    ref = create_specs()
    print ref

    wf = Workflow(ref)
    print wf

    tasks = wf.get_tasks(Task.READY)
    tasks[0].complete()

    tasks = wf.get_tasks(Task.READY)
    tasks[0].complete()
    tasks[1].complete()

    print wf.get_tasks(Task.READY)
