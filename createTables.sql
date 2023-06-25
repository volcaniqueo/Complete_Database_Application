CREATE TABLE user1 (
  username VARCHAR(100) PRIMARY KEY,
  password1 VARCHAR(100) NOT NULL,
  surname VARCHAR(100) NOT NULL,
  name1 VARCHAR(100) NOT NULL
);

CREATE TABLE audience (
  username VARCHAR(100) PRIMARY KEY REFERENCES user1 (username) ON DELETE CASCADE
);

CREATE TABLE director (
  username VARCHAR(100) PRIMARY KEY REFERENCES user1 (username) ON DELETE CASCADE,
  nationality VARCHAR(100) NOT NULL
);


CREATE TABLE rating_platform (
  platform_id SERIAL PRIMARY KEY,
  platform_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE movie (
  movie_id SERIAL PRIMARY KEY,
  movie_name VARCHAR(100) NOT NULL,
  duration INT NOT NULL CHECK (duration > 0),
  overall_rating INT
);

CREATE TABLE movie_session (
  session_id SERIAL PRIMARY KEY
);

CREATE TABLE theater (
  theater_id SERIAL PRIMARY KEY,
  theater_name VARCHAR(100) NOT NULL,
  theater_capacity INT NOT NULL CHECK (theater_capacity > 0),
  district VARCHAR(100) NOT NULL
);

CREATE TABLE genre (
  genre_id SERIAL PRIMARY KEY,
  genre_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE occupience_info (
  occupience_id SERIAL PRIMARY KEY,
  time1 VARCHAR(100) NOT NULL,
  slot_number INT NOT NULL,
  theater_id INT NOT NULL,
  UNIQUE (theater_id, slot_number, time1),
  CONSTRAINT CHK_SLOT CHECK (slot_number >= 1 AND slot_number <= 4),
  FOREIGN KEY (theater_id) REFERENCES theater (theater_id) ON DELETE CASCADE
);

CREATE TABLE database_manager (
  username VARCHAR(100) PRIMARY KEY,
  manager_number INT NOT NULL UNIQUE,
  password1 VARCHAR(100) NOT NULL,
  CHECK (manager_number >= 1 AND manager_number <= 4)
);

CREATE TABLE subscriptions (
  username VARCHAR(100) REFERENCES audience (username) ON DELETE CASCADE,
  platform_id INT REFERENCES rating_platform (platform_id) ON DELETE CASCADE,
  PRIMARY KEY (username, platform_id)
);

CREATE TABLE registered (
  username VARCHAR(100) REFERENCES director (username) ON DELETE CASCADE,
  platform_id INT REFERENCES rating_platform (platform_id) ON DELETE CASCADE,
  PRIMARY KEY (username, platform_id)
);

CREATE TABLE directs (
  username VARCHAR(100) REFERENCES director (username) ON DELETE CASCADE,
  movie_id INT REFERENCES movie (movie_id) ON DELETE CASCADE,
  PRIMARY KEY (movie_id),
  UNIQUE (movie_id, username)
);

CREATE TABLE ratings (
  rating_id SERIAL PRIMARY KEY,
  username VARCHAR(100) REFERENCES audience (username) ON DELETE SET NULL,
  movie_id INT NOT NULL REFERENCES movie (movie_id) ON DELETE CASCADE,
  rating INT NOT NULL,
  UNIQUE (username, movie_id)
);

CREATE TABLE genre_list (
  genre_id INT REFERENCES genre (genre_id) ON DELETE CASCADE,
  movie_id INT NOT NULL REFERENCES movie (movie_id) ON DELETE CASCADE,
  PRIMARY KEY (genre_id, movie_id)
);

CREATE TABLE place (
  session_id INT REFERENCES movie_session (session_id) ON DELETE CASCADE,
  occupience_id INT REFERENCES occupience_info (occupience_id),
  PRIMARY KEY (session_id,occupience_id),
  UNIQUE (occupience_id)
);

CREATE TABLE has_movie (
  session_id INT NOT NULL REFERENCES movie_session (session_id) ON DELETE CASCADE,
  movie_id INT REFERENCES movie (movie_id) ON DELETE NO ACTION,
  PRIMARY KEY (session_id, movie_id)
);

CREATE TABLE predecessors (
  predecessor_movie_id INT REFERENCES movie (movie_id) ON DELETE CASCADE,
  succeeds_movie_id INT REFERENCES movie (movie_id) ON DELETE CASCADE,
  PRIMARY KEY (predecessor_movie_id, succeeds_movie_id)
);

CREATE TABLE bought_tickets (
  username VARCHAR(100) REFERENCES audience (username) ON DELETE CASCADE,
  session_id INT REFERENCES movie_session (session_id) ON DELETE CASCADE,
  PRIMARY KEY (username, session_id)
);

CREATE FUNCTION ratings_bought_ticket() RETURNS TRIGGER AS $$
BEGIN
  IF NOT EXISTS (
      SELECT 1 
      FROM bought_tickets, has_movie
      WHERE bought_tickets.session_id  = has_movie.session_id AND new.movie_id = has_movie.movie_id  and username = NEW.username
    ) THEN
    RAISE EXCEPTION 'The audience did not buy any ticket for any session for this movie';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ratings_bought_ticket_trigger
BEFORE INSERT ON ratings
FOR EACH ROW
EXECUTE FUNCTION ratings_bought_ticket();

CREATE FUNCTION update_movie_rating()
RETURNS TRIGGER AS $$
DECLARE
  avg_rating DECIMAL;
BEGIN
  -- Calculate the average rating for the movie
	SELECT AVG(rating)
	INTO avg_rating
	from ratings 
	where ratings.movie_id = new.movie_id
	group by ratings.movie_id;
  -- Update the overall rating of the movie in the ratings table
  UPDATE movie
  SET overall_rating = avg_rating
  WHERE movie_id = NEW.movie_id;

  RETURN NULL; -- We don't need to return anything for a trigger function
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_movie_rating_trigger
AFTER INSERT ON ratings
FOR EACH ROW
EXECUTE FUNCTION update_movie_rating();

CREATE TRIGGER update_movie_rating_trigger_2
AFTER UPDATE ON ratings
FOR EACH ROW
EXECUTE FUNCTION update_movie_rating();

CREATE FUNCTION check_two_roles_constraint_audience() RETURNS TRIGGER AS $$
DECLARE 
  user_type VARCHAR(10);
BEGIN
  user_type := NULL;

  IF EXISTS (SELECT 1 FROM director WHERE username = NEW.username) THEN
    user_type := 'director';
  END IF;

  IF user_type = 'director' THEN
    RAISE EXCEPTION 'User is already defined as director!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_two_roles_constraint_trigger_audience
BEFORE INSERT ON audience
FOR EACH ROW
EXECUTE FUNCTION check_two_roles_constraint_audience();

CREATE FUNCTION check_two_roles_constraint_director() RETURNS TRIGGER AS $$
DECLARE 
  user_type VARCHAR(10);
BEGIN
  user_type := NULL;

  IF EXISTS (SELECT 1 FROM audience WHERE username = NEW.username) THEN
    user_type := 'audience';
  END IF;

  IF user_type = 'audience' THEN
    RAISE EXCEPTION 'User is already defined as audience!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_two_roles_constraint_trigger_director
BEFORE INSERT ON director
FOR EACH ROW
EXECUTE FUNCTION check_two_roles_constraint_director();

CREATE FUNCTION ratings_platform_match() RETURNS TRIGGER AS $$
BEGIN
  IF NOT EXISTS (
      SELECT 1 FROM subscriptions
      WHERE username = NEW.username
        AND platform_id = (
          SELECT platform_id FROM registered WHERE username = (
            SELECT username FROM directs WHERE movie_id = NEW.movie_id
          )
        )
    ) THEN
    RAISE EXCEPTION 'The audience is not subscribed to the rating platform that the movie director is registered to!';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ratings_platform_match_trigger
BEFORE INSERT ON ratings
FOR EACH ROW
EXECUTE FUNCTION ratings_platform_match();