import datetime
import hashlib
import logging


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        str(phone) if phone else "",
        datetime.datetime.strptime(birthday, '%d.%m.%Y').date().strftime("%Y%m%d")
        if birthday is not None else "",
        ]
    key = "uid:" + hashlib.md5("".join(key_parts).encode('utf-8')).hexdigest()
    logging.info('Key: %s', key)
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        logging.info('The value from cache found, will be returned')
        return score
    logging.info('Getting value in cache failed, calculating...')
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender is not None:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    return r if r else []
