import json
import pytest

from .. import load_tabby


@pytest.fixture(scope="session")
def tabby_framed_record(tmp_path_factory):
    rdir = tmp_path_factory.mktemp("rec")
    dataset = rdir / 'rec_dataset.tsv'
    dataset.write_text(
        # empty line up top
        "name\tmydataset\n"
        "author\t@tabby-many-authors\n"
    )
    authors = rdir / 'rec_authors.tsv'
    authors.write_text(
        "name\temail\n"
        "Michael\tmih@example.com\n"
        "\tignored@example.com\n"
    )
    dataset_context = rdir / 'rec_dataset.ctx.jsonld'
    dataset_context.write_text(json.dumps({
        'schema': 'https://schema.org/',
        'name': 'schema:name',
        'email': 'schema:email',
        'author': 'schema:author',
        'Person': 'schema:Person',
    }))
    dataset_frame = rdir / 'rec_dataset.frame.jsonld'
    dataset_frame.write_text(json.dumps({
        # we do not put a @context here (although we could),
        # because defining the vocab is not our goal here
        'author': {
            'name': {},
            'type': {'@default': 'Person'},
        }
    }))
    yield dict(
        input=dict(
            dataset=dataset,
            authors=authors,
            context=dataset_context,
            frame=dataset_frame,
        ),
    )


def test_load_tabby_framing(tabby_framed_record):
    # first just the structure, but no definitions
    nonld = load_tabby(
        tabby_framed_record['input']['dataset'],
        single=True,
        jsonld=False,
    )
    assert '@context' not in nonld
    assert all('@type' not in a for a in nonld['author'])
    # again, this time going all semantic
    ld = load_tabby(
        tabby_framed_record['input']['dataset'],
        single=True,
        jsonld=True,
    )
    assert '@context' in ld
    assert ld['author'][0]['name'] == 'Michael'
    assert ld['author'][0]['@type'] == 'Person'
    # check that we get no type infusion where the frame did not match
    assert '@type' not in ld['author'][1]
    breakpoint()
