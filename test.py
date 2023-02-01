
class Todo():
    '''
    DB table
    '''
    id = 324234234234

    def __repr__(self):
        a = '<Task %r>' % self.id
        return a




if __name__ == "__main__":

    task = Todo()

    print("start!")
    print(task.__repr__())



