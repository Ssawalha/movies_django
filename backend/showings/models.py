from django.db import models

# TODO ADD TIMESTAMP MIXIN

class Location(models.Model):
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    website = models.URLField(null=True)

    def __str__(self):
        return f"{self.name} - {self.address}"


class Batch(models.Model):
    batch_id = models.CharField(max_length=100)
    showings = models.ManyToManyField('Showing', related_name='batch')
    movies = models.ManyToManyField('Movie', related_name='batch')
    status = models.CharField(max_length=100) # statuscode?

    def __str__(self):
        return f"{self.batch_id}"


class Movie(models.Model):
    title = models.CharField(max_length=100)
    
    # missing: taj (take from imdb)
    # do they match for grand and prime?
    genre = models.CharField(max_length=100, null=True)
    
    # missing: prime taj grand
    #rating = models.CharField(max_length=100, null=True)
    
    # DOES NOT MATCH!
    # runtime = models.DurationField(null=True)

    # TODO FUTURE FEATURE
    # poster = models.URLField(null=True) # never matches, take from taj, else grand, else prime

    # missing: prime
    trailer = models.URLField(null=True) # taj and grand trailer links can match for arabic

    # missing: prime grand
    # can be detected I think. 
    # if language is arabic then take imdb name from grand
    language = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class Showing(models.Model):
    movie = models.ForeignKey(Movie, related_name='showings', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='showings', on_delete=models.CASCADE)
    url = models.URLField(null=True)
    date = models.DateField()
    time = models.TimeField()
    is_showing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.movie.title} - {self.url}"
