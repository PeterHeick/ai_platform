import mongoose, { Schema, Model, PassportLocalModel, PassportLocalDocument } from 'mongoose';
import passportLocalMongoose from 'passport-local-mongoose';

interface IUser extends PassportLocalDocument {
  username: string;
}

const UserSchema: Schema<IUser & PassportLocalDocument> = new Schema({
  username: { type: String, required: true, unique: true },
});

UserSchema.plugin(passportLocalMongoose);
// UserSchema.plugin(passportLocalMongoose, {
//   usernameField: 'username',
// });

const User: PassportLocalModel<IUser> = mongoose.model<IUser>('User', UserSchema);

export { User, IUser };

// Definerer en interface for PassportUserModel, som passport-local-mongoose forventer
interface PassportUserModel<TUser extends PassportLocalDocument> extends Model<TUser> {
  authenticate(): (username: string, password: string, done: (error: any, user?: TUser, options?: any) => void) => void;
  serializeUser(): (user: TUser, done: (err: any, id?: any) => void) => void;
  deserializeUser(): (id: string, done: (err: any, user?: TUser) => void) => void;
}

// Definerer en ny type, der implementerer PassportUserModel
type UserModel = PassportUserModel<IUser>;

export { UserModel };
