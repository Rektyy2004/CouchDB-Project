{
  "_id": "_design/movies",
  "language": "javascript",
  "views": {
    "by_title": {
      "map": function (doc) {
        var t = doc.title || doc.Title || doc.movie_title || doc.name || doc.Series_Title ||
                doc.primaryTitle || doc.original_title || doc.originalTitle ||
                doc["\ufefftitle"] || doc["\ufeffTitle"] || doc["\ufeffname"] || doc["\ufeffSeries_Title"];

        if (!t) return;

        t = String(t).trim().toLowerCase();
        emit(t, null);
      },
      "reduce": "none"
    },

    "by_year": {
      "map": function (doc) {
        var y = parseInt(doc.year || doc.Year, 10);
        if (!isNaN(y)) emit(y, null);
      },
      "reduce": "none"
    },

    "by_year_count": {
      "map": function (doc) {
        var y = parseInt(doc.year || doc.Year, 10);
        if (!isNaN(y)) emit(y, 1);
      },
      "reduce": "_count"
    },

    "rating_stats_by_genre": {
      "map": function (doc) {
        function num(x) {
          if (x === undefined || x === null) return null;

          var ratingMap = {
            "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4
          };

          if (typeof x === "string") {
            return ratingMap[x] || null;
          }

          var s = String(x).replace(/,/g, '');
          var n = parseFloat(s);
          return isNaN(n) ? null : n;
        }

        var r = num(doc.rating || doc.Rating || doc.imdb_rating || doc.averageRating || doc.imdbRating);
        if (r == null) return;

        var g = doc.genre || doc.Genre || doc.listed_in || doc.categories;
        if (!g) return;

        // Emit the genre directly if it's a single genre
        var arr = Array.isArray(g) ? g : [String(g).trim()];
        for (var i = 0; i < arr.length; i++) {
          var x = arr[i] || '';
          if (x) emit([x], r);
        }
      },
      "reduce": "_stats"
    },

    "rating_stats_by_genre_year": {
      "map": function (doc) {
        function num(x) {
          if (x === undefined || x === null) return null;

          var s = String(x).trim();
          if (/%$/.test(s)) { // "87%"
            var p = parseFloat(s.replace('%', ''));
            return isNaN(p) ? null : p / 10; // Normalize to 0-10 scale
          }

          s = s.replace(/,/g, ''); // Remove commas from "8,7" or "1,234"
          var m = s.match(/-?\d+(\.\d+)?/); // Extract number from strings like "8.7/10"
          if (!m) return null;

          var n = parseFloat(m[0]);
          return isNaN(n) ? null : n;
        }

        function pickYear(d) {
          var cands = [d.year, d.Year, d.release_year, d.releaseYear, d.premiered, d.release_date, d.date];
          for (var i = 0; i < cands.length; i++) {
            var v = cands[i];
            if (v === undefined || v === null) continue;
            var s = String(v);
            var m = s.match(/\b(19|20)\d{2}\b/);
            if (m) return parseInt(m[0], 10);
          }
          return NaN;
        }

        var r = num(doc.rating || doc.Rating || doc.imdb_rating || doc.averageRating || doc.imdbRating || doc.score || doc.vote_average);
        var y = pickYear(doc);
        if (r == null || isNaN(y)) return;

        var g = doc.genres || doc.Genres || doc.genre || doc.Genre || doc.listed_in || doc.categories;
        if (!g) return;

        var arr = Array.isArray(g) ? g : String(g).split(/[,;/|]/);
        for (var i = 0; i < arr.length; i++) {
          var x = String(arr[i] || '').trim();
          if (x) emit([x, y], r);
        }
      },
      "reduce": "_stats"
    },

    "votes_by_year_sum": {
      "map": function (doc) {
        function toInt(x) {
          if (x === undefined || x === null) return NaN;
          var s = String(x).replace(/,/g, '');
          return parseInt(s, 10);
        }

        var y = parseInt(doc.year || doc.Year, 10);
        var v = toInt(doc.votes || doc.Votes || doc.vote_count || doc.imdb_votes || doc.numVotes);
        if (!isNaN(y) && !isNaN(v)) emit(y, v);
      },
      "reduce": "_sum"
    }
  }
}
