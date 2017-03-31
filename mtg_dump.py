#!/usr/bin/env python
import time
from argparse import ArgumentParser

from mtg_api.my_database import MyDatabase
from mtg_api.db import setup_database
from mtg_api.config import Config, init as config_init


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('sets', nargs='*',
                    help='The set codes of the sets to process. If none are provided, all sets will be processed.')
    p.add_argument('-i', '--invert', required=False, action='store_true', default=False,
                    help='Invert the given set codes such that all sets EXCEPT those will be processed.')
    p.add_argument('-f', '--force', required=False, action='store_true',
                    help='Add sets/cards even if matching sets/cards already exist in the database.\
                          Often used with --drop to refresh the database completely.')
    p.add_argument('--commit-interval', default=500, action='store', type=int,
                    help='Determines how many objects to aggregate in a session before committing them to the DB. A larger\
                          value may speed up the process, but it may incur database timeout errors.')
    p.add_argument('--drop', action='store_true',
                    help='Drop all tables and recreate them from the models before doing any processing.')
    p.add_argument('-o', '--overwrite', action='store_true',
                    help='Overwrite any existing cards or sets that would be added. (May significantly increase processing time)')
    p.add_argument('--dry', action='store_true', default=False,
                    help='Adding this flag prevents any database operations from actually being committed (primarily for debugging).')
    p.add_argument('-c', '--config', action="store", default="test", help="The config file to use for connecting to the database. ('test' or 'live')")

    args = p.parse_args()


    config_init(args.config.lower())
    if args.config == "test":
        config = Config(Config.TEST_CONFIG_PATH, True)
    elif args.config == "live":
        config = Config(Config.LIVE_CONFIG_PATH, True)
    else:
        raise StandardError("--config should be one of 'test' or 'live'.")
    db = MyDatabase(config)
    setup_database(db)

    from mtg_api.DATA.card_data_handler import get_raw_card_data
    from mtg_api.DATA.process_data import *
    from mtg_api.models.magic import MtgCardSetModel

    if args.drop and not args.dry:
        db.drop_tables()
        db.make_tables()
    if args.sets:
        sets = [s for s in get_raw_card_data().keys() if (args.invert and s not in args.sets) or (not args.invert and s in args.sets)]
    else:
        sets = get_raw_card_data().keys()
    if not args.force:
        existing_sets = MtgCardSetModel.filter(MtgCardSetModel.code.in_(sets)).all()
        existing_sets = [s.code for s in existing_sets]
        if existing_sets and not args.force:
            print('These sets already existing the database, ignoring... \
                  (use --force to add them anyway, or --overwrite to overwrite)\n{sets}'.format(sets=', '.join(existing_sets)))
            sets = [s for s in sets if s not in existing_sets]

    # TODO Make --force and --overwrite relevant
    try:
        start = time.time()
        if not args.dry:
            prep_mana_symbols()
            for s in sets:
                data = do_data_process(s)
                mysql_dump(data, commit_interval=args.commit_interval)
    except KeyboardInterrupt:
        print 'Rolling back before exit!'
        db.Session.rollback()
        raise
    print 'Total processing time: {time}'.format(time=time.time()-start)
