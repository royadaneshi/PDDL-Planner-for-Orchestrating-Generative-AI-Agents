import re
from typing import Any
import variables


def tokenise(text: str) -> list[str]:
    text = re.sub(r';[^\n]*', '', text)
    text = text.replace('(', ' ( ').replace(')', ' ) ')
    return text.split()


def parse_sexp(tokens: list[str]) -> Any:
    if not tokens:
        raise SyntaxError("Unexpected end of token stream")

    token = tokens.pop(0)

    if token == '(':
        sexp = []
        while tokens[0] != ')':
            sexp.append(parse_sexp(tokens))
        tokens.pop(0)  # consume the closing ')'
        return sexp
    elif token == ')':
        raise SyntaxError("Unexpected ')'")
    else:
        return token.lower()


def parse_pddl_file(path: str) -> list[Any]:
    with open(path, 'r') as fh:
        text = fh.read()
    tokens = tokenise(text)
    return parse_sexp(tokens)


def find_section(sexp: list[Any], keyword: str) -> list[Any]:
    for item in sexp:
        if isinstance(item, list) and item and item[0] == keyword:
            return item
    return []


def find_all_sections(sexp: list[Any], keyword: str) -> list[list[Any]]:
    return [item for item in sexp if isinstance(item, list) and item and item[0] == keyword]


def parse_literal_list(sexp: Any) -> list[tuple[bool, str, list[str]]]:
    literals: list[tuple[bool, str, list[str]]] = []

    def _extract(expr: Any) -> None:
        if not isinstance(expr, list) or not expr:
            return
        head = expr[0]
        if head == 'and':
            for child in expr[1:]:
                _extract(child)
        elif head == 'not':
            inner = expr[1]
            if isinstance(inner, list) and inner:
                literals.append((False, inner[0], inner[1:]))
        else:
            literals.append((True, head, expr[1:]))

    _extract(sexp)
    return literals


def parse_action_schema(action_sexp: list[Any]) -> dict[str, Any]:
    name = action_sexp[1]
    params: list[tuple[str, str | None]] = []
    preconds: list[tuple[bool, str, list[str]]] = []
    add_effs: list[tuple[str, list[str]]] = []
    del_effs: list[tuple[str, list[str]]] = []

    i = 2
    while i < len(action_sexp):
        key = action_sexp[i]
        if key == ':parameters':
            param_list = action_sexp[i + 1]
            j = 0
            while j < len(param_list):
                p = param_list[j]
                if j + 1 < len(param_list) and param_list[j + 1] == '-':
                    ptype = param_list[j + 2] if j + 2 < len(param_list) else None
                    params.append((p, ptype))
                    j += 3
                else:
                    params.append((p, None))
                    j += 1
            i += 2
        elif key == ':precondition':
            preconds = parse_literal_list(action_sexp[i + 1])
            i += 2
        elif key == ':effect':
            all_lits = parse_literal_list(action_sexp[i + 1])
            for positive, pred, args in all_lits:
                if positive:
                    add_effs.append((pred, args))
                else:
                    del_effs.append((pred, args))
            i += 2
        else:
            i += 1

    return {
        'name': name,
        'parameters': params,
        'preconditions': preconds,
        'add_effects': add_effs,
        'del_effects': del_effs,
    }


def parse_domain(domain_path: str) -> dict[str, Any]:
    sexp = parse_pddl_file(domain_path)
    action_sexps = find_all_sections(sexp, ':action')
    return {'actions': [parse_action_schema(a) for a in action_sexps]}


def parse_problem(problem_path: str) -> dict[str, Any]:
    sexp = parse_pddl_file(problem_path)
    init_section = find_section(sexp, ':init')
    init_facts: set[str] = set()

    for item in init_section[1:]:
        if isinstance(item, list) and item:
            init_facts.add(ground_fact_to_str(item[0], item[1:]))

    return {'init': frozenset(init_facts)}


def parse_plan(plan_path: str) -> list[str]:
    actions: list[str] = []
    with open(plan_path, 'r') as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith(';'):
                continue
            line = line.split(';')[0].strip()
            if not line:
                continue
            colon_idx = line.find(':')
            if colon_idx != -1 and line[:colon_idx].replace('.', '').isdigit():
                line = line[colon_idx + 1:].strip()
            line = line.lower()
            if line:
                actions.append(line)
    return actions


def parse_ground_action(action_str: str) -> tuple[str, list[str]]:
    parts = action_str.strip().strip('()').split()
    return parts[0], parts[1:]


def ground_fact_to_str(predicate: str, args: list[str]) -> str:
    if args:
        return f"{predicate} {' '.join(args)}"
    return predicate


def ground_schema(schema: dict[str, Any], bindings: dict[str, str]) -> dict[str, Any]:
    def sub(args: list[str]) -> list[str]:
        return [bindings.get(a, a) for a in args]

    return {
        'name': schema['name'],
        'preconditions': [(pos, pred, sub(args)) for pos, pred, args in schema['preconditions']],
        'add_effects': [(pred, sub(args)) for pred, args in schema['add_effects']],
        'del_effects': [(pred, sub(args)) for pred, args in schema['del_effects']],
    }


def match_schema_to_action(
        schema: dict[str, Any],
        action_name: str,
        action_args: list[str],
) -> dict[str, str] | None:
    if schema['name'] != action_name:
        return None
    param_names = [p for p, _ in schema['parameters']]
    if len(param_names) != len(action_args):
        return None
    return dict(zip(param_names, action_args))


def ground_plan_actions(
        domain: dict[str, Any],
        plan_actions: list[str],
) -> list[dict[str, Any]]:
    grounded: list[dict[str, Any]] = []
    for step, action_str in enumerate(plan_actions):
        act_name, act_args = parse_ground_action(action_str)
        matched = None
        for schema in domain['actions']:
            bindings = match_schema_to_action(schema, act_name, act_args)
            if bindings is not None:
                matched = ground_schema(schema, bindings)
                break
        if matched is None:
            matched = {
                'name': act_name,
                'preconditions': [],
                'add_effects': [],
                'del_effects': [],
            }
        matched['label'] = action_str.strip('()')
        matched['step'] = step
        grounded.append(matched)
    return grounded


def simulate_plan(grounded_actions: list[dict[str, Any]], init_facts: frozenset[str], ) -> list[frozenset[str]]:
    states: list[frozenset[str]] = [init_facts]
    current: set[str] = set(init_facts)

    for action in grounded_actions:
        for pred, args in action['del_effects']:
            current.discard(ground_fact_to_str(pred, args))
        for pred, args in action['add_effects']:
            current.add(ground_fact_to_str(pred, args))
        states.append(frozenset(current))

    return states


def find_producer(grounded_actions: list[dict[str, Any]], states: list[frozenset[str]], fact: str, consumer_idx: int,
                  ) -> tuple[int | None, bool]:
    for idx in range(consumer_idx - 1, -1, -1):
        action = grounded_actions[idx]
        add_facts = {ground_fact_to_str(p, a) for p, a in action['add_effects']}
        del_facts = {ground_fact_to_str(p, a) for p, a in action['del_effects']}

        if fact in del_facts:
            if fact in add_facts:
                return idx, False
            return None, False

        if fact in add_facts:
            return idx, False

    if fact in states[0]:
        return None, True

    return None, False


def extract_causal_links(domain_path: str, problem_path: str, plan_path: str, ) -> list[dict[str, str]]:
    domain = parse_domain(domain_path)
    problem = parse_problem(problem_path)
    plan_actions_raw = parse_plan(plan_path)
    grounded_actions = ground_plan_actions(domain, plan_actions_raw)
    states = simulate_plan(grounded_actions, problem['init'])

    causal_links: list[dict[str, str]] = []
    seen: set[tuple[int | str, int, str]] = set()

    for consumer_idx, consumer in enumerate(grounded_actions):
        state_before = states[consumer_idx]

        for pos, pred, args in consumer['preconditions']:
            if not pos:
                continue
            fact = ground_fact_to_str(pred, args)

            if fact not in state_before:
                continue

            producer_idx, is_init = find_producer(
                grounded_actions, states, fact, consumer_idx
            )

            if producer_idx is not None:
                producer_label = grounded_actions[producer_idx]['label']
                dedup_key: tuple[int | str, int, str] = (producer_idx, consumer_idx, fact)
            elif is_init:
                producer_label = '__init__'
                dedup_key = ('__init__', consumer_idx, fact)
            else:
                continue
            if dedup_key not in seen:
                seen.add(dedup_key)
                causal_links.append({
                    'producer': producer_label,
                    'consumer': consumer['label'],
                    'fact': fact,
                })

    return causal_links


def format_link(link: dict[str, str]) -> str:
    return f"({link['producer']}) --[{link['fact']}]--> ({link['consumer']})"


def causal_extractor() -> list[dict[str, str]]:
    domain_path = variables.PDDL_DOMAIN_PATH
    problem_path = variables.PDDL_PROBLEM_PATH
    plan_path = variables.PDDL_PLAN_PATH
    links = extract_causal_links(domain_path, problem_path, plan_path)

    if links:
        print(f"\nFound {len(links)} causal link(s):\n")
        for link in links:
            print(f"  {format_link(link)}")
    else:
        print("\nNo causal links found.")

    return links
